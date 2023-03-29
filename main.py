import argparse
import os
import sys

coref_path = os.path.join(os.path.dirname(__file__), 'coref_resolution')
quote_path = os.path.join(os.path.dirname(__file__), 'quote_attr')
sys.path.extend([coref_path, quote_path])

from coref_resolution.main import Coref
from quote_attr.attribute_quotes import attribute_quotes_file

class Pipeline:
    def __init__(self, filepath, output_dir) -> None:
        self.filepath = os.path.abspath(filepath)
        self.fname = os.path.splitext(os.path.basename(self.filepath))[0]
        self.output_dir = os.path.abspath(output_dir)
        self.quote_dir = os.path.join(self.output_dir, "quote_attr")
        self.coref_dir = os.path.join(self.output_dir, "coref")

    def coref_resolution(self):
         cwd = os.getcwd()
         os.chdir(coref_path)
         coref = Coref(self.filepath, self.coref_dir)
         coref.run()
         os.chdir(cwd)

    
    def quote_attr(self):
         cwd = os.getcwd()
         os.chdir(quote_path)
         fdir = os.path.dirname(self.filepath)
         attribute_quotes_file(self.fname, fdir, self.coref_dir, self.quote_dir)
         os.chdir(cwd)
    
    def run(self):
         print("Starting pipleine..")
         self.coref_resolution()
         print("Quote Attribution begun..")
         self.quote_attr()
         print("Complete")
    


def get_args():
     parser = argparse.ArgumentParser()
     parser.add_argument('--filepath', type=str, required=True,
                    help='Path of input file')
     parser.add_argument('--output_dir', type=str, required=True,
                    help='Output Dir')
     return parser


if __name__ == "__main__":
     parser = get_args()
     args = parser.parse_args()
     pipeline = Pipeline(args.filepath, args.output_dir)
     pipeline.run()
