import argparse
import os
import sys
import time
import resource

coref_path = os.path.join(os.path.dirname(__file__), 'coref_resolution')
quote_path = os.path.join(os.path.dirname(__file__), 'quote_attr')
voice_path = os.path.join(os.path.dirname(__file__), 'voice_synthesis')
sys.path.extend([coref_path, quote_path])

from coref_resolution.main import Coref
from quote_attr.attribute_quotes import attribute_quotes_file
import metrics


class Pipeline:
     def __init__(self, filepath, output_dir, args) -> None:
          self.filepath = os.path.abspath(filepath)
          self.fname = os.path.splitext(os.path.basename(self.filepath))[0]
          self.output_dir = os.path.abspath(output_dir)
          self.quote_dir = os.path.join(self.output_dir, "quote_attr")
          self.coref_dir = os.path.join(self.output_dir, "coref")
          self.voice_dir = os.path.join(self.output_dir, "voice")
          self.args = args
          self.time=0

     def coref_resolution(self):
          cwd = os.getcwd()
          os.chdir(coref_path)
          coref = Coref(self.filepath, self.coref_dir, self.args.is_conll)
          coref.run()
          self.time=coref.time
          self.max_memory_alloc = coref.max_memory_alloc
          os.chdir(cwd)


     def quote_attr(self):
          cwd = os.getcwd()
          os.chdir(quote_path)
          fdir = os.path.dirname(self.filepath)
          attribute_quotes_file(self.fname, fdir, self.coref_dir, self.quote_dir)
          os.chdir(cwd)

     def voice_syn(self):
          from voice_synthesis.main import VoiceSynthesizer
          cwd = os.getcwd()
          os.chdir(voice_path)
          voicer = VoiceSynthesizer(os.path.join(self.quote_dir, self.fname+".json"), os.path.join(self.coref_dir, self.fname+".json"), self.voice_dir, self.args.gen_voice_files)
          voicer.run()
          os.chdir(cwd)
     
     def metrics(self):
          metrics.run(os.path.join(self.quote_dir, self.fname+".json"), self.args.metrics, self.args.character_data)

     def run(self):
          print("Starting pipleine..")
          self.coref_resolution()
          print("Quote Attribution begun..")
          self.quote_attr()
          if self.args.gen_voice:
                    print("Voice Synthesis begun..")
                    self.voice_syn()
          if self.args.metrics:
               self.metrics()
          print("Time: ", time.time()-self.time)
          print("Peak CPU memory used: ", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
          print("Peak GPU memory used: ", self.max_memory_alloc / (1024 ** 3))

          print("Complete")
    


def get_args():
     parser = argparse.ArgumentParser()
     parser.add_argument('--filepath', type=str, required=True,
                    help='Path of input file')
     parser.add_argument('--output_dir', type=str, required=True,
                    help='Output Dir')
     parser.add_argument('--gen_voice', type=lambda x: (str(x).lower() == 'true'), required=False,
                    default = True, help='Set True if you want to generate voice.')
     parser.add_argument('--gen_voice_files', type=lambda x: (str(x).lower() == 'true'), required=False,
                    default = False, help='Set True if you want to generate voice for each quote seperately.')
     parser.add_argument('--is_conll', type=str, required=False,
                    default = False, help='Should be set True if input is a conll format file.')
     parser.add_argument('--metrics', type=str, required=False,
                    default = None, help='Should be set if metrics are needed.')
     parser.add_argument('--character_data', type=str, required=False,
                    default = None, help='Should be set if metrics are needed.')
     return parser


if __name__ == "__main__":
     os.environ['TOKENIZERS_PARALLELISM']="false"
     parser = get_args()
     args = parser.parse_args()
     pipeline = Pipeline(args.filepath, args.output_dir, args)
     pipeline.run()
