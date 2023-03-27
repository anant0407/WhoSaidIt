import argparse
from . import minimize
import os
from . import convert_txt_to_conll
def gen_connl(fpath, output_dir):
    convert_txt_to_conll.convert(fpath, output_dir)
    pass

def gen_jsonlines(fpath, output_dir):
    preprocess_params = ['--filename', fpath, '--output_dir', output_dir]
    preprocess_argparser = minimize.get_argparser()
    preprocess_args = preprocess_argparser.parse_args(preprocess_params)
    minimize.minimize_language(preprocess_args)
    pass

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True,
                        help='Name of file')
    parser.add_argument('--tokenizer_name', type=str, default='bert-large-cased',
                        help='Name or path of the tokenizer/vocabulary')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Output Dir')
    parser.add_argument("--conll_dir", type=str, required=True,
                        help='Directory for saving conll file')
    parser.add_argument('--raw_text', type=bool, default=False,
                        help='Should be set as true, if input is raw text.')
    return parser

if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()

    gen_connl(args.filename, args.output_dir)
    fname=os.path.splitext(os.path.basename(args.filename))[0]
    conll_path=os.path.join(args.conll_dir, fname+".conll")
    gen_jsonlines(conll_path, args.output_dir)