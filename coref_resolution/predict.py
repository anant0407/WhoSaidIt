import logging
import json

from tqdm import tqdm
import torch

import time

import util

from model.incremental import Incremental
from model.cluster import ClusterList

class Predictor():
  def __init__(self, model, data, singleton_eval):
    self.model = model
    self.data = data
    self.singleton_eval = singleton_eval
    self.reset()

  def reset(self):
    self.model.reset_metrics()
    self.predictions = []
    if torch.cuda.is_available():
      torch.cuda.reset_peak_memory_stats()

  def predict(self, write_file=None, perf=False):
    self.reset()
    self.predictions = []
    self.model = self.model.eval()
    self.perf_data = []
    start_time = time.time()
    eval_iterator = tqdm(enumerate(self.data))
    total_loss = []
    for doc_id, document in eval_iterator:
      cluster_list, loss = self.incremental_clustering(document)
      predicted_clusters = cluster_list.get_clusters(self.singleton_eval, condensed=True, print_clusters=False)
      self.predictions.append(predicted_clusters)
      if perf and torch.cuda.is_available():
        max_memory_alloc = torch.cuda.max_memory_allocated() / (1024 ** 3)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
        self.perf_data.append((document["subtoken_map"][-1], max_memory_alloc))
      eval_iterator.set_description_str(desc=f"{loss:.4f}")
      total_loss.append(loss)
    avg_loss = sum(total_loss) / len(total_loss) if len(total_loss) != 0 else 0
    end_time = time.time()
    logging.info(f"Evaluation on {len(self.data)} documents [{avg_loss:.3f}] took {end_time - start_time:.1f} seconds")

    if(write_file !=None ):
      self.write_preds(write_file)
      logging.info(f"Wrote preds to {write_file}")
    return self.predictions


  def incremental_clustering(self, document):
    total_clusters = ClusterList()
    num_runs = 1
    for run in range(num_runs):
      total_clusters.reset()
      # For gradual thresholding (unused)
      # self.model.set_threshold(1 * (num_runs - 1 - run))
      loss = 0.0
      start_idx = 0
      segment_iter = util.get_segment_iter(document)
      for seg_id, (segment, mask, seglen) in segment_iter:
        loss += self.model(segment, document, total_clusters, start_idx, mask,
                           metrics=(run == num_runs - 1),
                           consolidate=(seg_id == 0))
        start_idx += seglen
        self.model.clear_cache(total_clusters, start_idx)
    total_clusters.cpu_()
    return total_clusters, loss

  def write_preds(self, path):
    preds_file = open(path, 'w+')
    for document, preds in zip(self.data, self.predictions):
      document["predicted_clusters"] = preds["clusters"]
      if self.model.debug_embs:
        document["span_embs"] = preds["span_embs"]
        document["cluster_embs"] = preds["cluster_embs"]
      document_write = dict(document)
      del document_write["antecedent_map"]
      preds_file.write(json.dumps(document_write) + "\n")
    preds_file.close()



if __name__ == "__main__":
  config = util.initialize_from_json()
  data_prefix = "test" if config["test_set"] else "dev"
  incremental_model = Incremental(config)
  if config.get("preload_path") is not None:
      util.load_params(incremental_model, config["preload_path"], "model")
  if config["load_model"]:
      util.load_params(incremental_model, config["load_path"], "model")
  logging.info(f"Updating threshold to {config['threshold']}")
  incremental_model.set_threshold(config["threshold"])

  eval_data = util.load_data(config[f"{data_prefix}_path"], config.get("num_dev_examples"))

  predictor = Predictor(incremental_model, eval_data, config["singleton_eval"])

  with torch.no_grad():
      predictor.predict(write_file=config["log_dir"] + f"/{data_prefix}_preds.json", perf=True)