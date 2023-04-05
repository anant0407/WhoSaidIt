import argparse
import os
from preprocess.main import gen_connl, gen_jsonlines
import util
import logging
from model.incremental import Incremental
from predict import Predictor
import torch
import post_process.main as postprocess
import time
class Coref:
    def __init__(self, input_file, output_dir, is_conll) -> None:
        self.input_file = input_file
        self.fname=os.path.splitext(os.path.basename(self.input_file))[0]
        self.temp_dir = os.path.join(output_dir, "temp")
        self.conll_dir = os.path.join(self.temp_dir,"conll")
        self.jsonlines_dir = os.path.join(self.temp_dir, "jsonlines")
        self.preds_dir= os.path.join(self.temp_dir, "preds")
        self.output_dir = output_dir
        self.is_conll = is_conll
        self.time = 0

    def preprocess(self):

        if self.is_conll:
            gen_jsonlines(self.input_file, self.jsonlines_dir)
            self.jsonlines_path = os.path.join(self.jsonlines_dir, self.fname+".jsonlines")
            return

        gen_connl(self.input_file, self.conll_dir)
        conll_path=os.path.join(self.conll_dir, self.fname+".conll")
        gen_jsonlines(conll_path, self.jsonlines_dir)
        self.jsonlines_path = os.path.join(self.jsonlines_dir, self.fname+".jsonlines")
        pass

    def predict(self):
        config = util.initialize_from_json()
        incremental_model = Incremental(config)
        if config.get("preload_path") is not None:
            util.load_params(incremental_model, config["preload_path"], "model")
        if config["load_model"]:
            util.load_params(incremental_model, config["load_path"], "model")
        logging.info(f"Updating threshold to {config['threshold']}")
        incremental_model.set_threshold(config["threshold"])

        eval_data = util.load_data(self.jsonlines_path, config.get("num_dev_examples"))

        predictor = Predictor(incremental_model, eval_data, config["singleton_eval"])

        if not os.path.exists(self.preds_dir):
            os.makedirs(self.preds_dir)

        with torch.no_grad():
            
            self.time = time.time()
            predictor.predict(write_file=os.path.join(self.preds_dir, self.fname + ".json"), perf=True)
            self.preds_path = os.path.join(self.preds_dir, self.fname + ".json")
            self.max_memory_alloc = predictor.max_memory_alloc
    
    def postprocess(self):
        self.infered_dir = os.path.join(self.temp_dir, "infered")
        postprocess.run(self.preds_path, self.infered_dir, self.output_dir)


    def run(self):
        self.preprocess()
        print("Preprocessing done..")
        self.predict()
        print("Predicting done..")
        self.postprocess()
        print("Post processing done..")

def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('--filepath', type=str, required=True,
                        help='Path of input file')
        parser.add_argument('--output_dir', type=str, required=True,
                        help='Output Dir')
        parser.add_argument('--is_conll', type=lambda x: (str(x).lower() == 'true'), default=False,
                        help='Should be set as true, if input is a conll format file.')
        return parser

if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()
    coref = Coref(args.filepath, args.output_dir, args.is_conll)
    coref.run()

