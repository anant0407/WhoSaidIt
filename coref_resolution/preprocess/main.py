import argparse

def gen_connl():
    pass

def gen_jsonlines():
    pass

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True,
                        help='Name of file')
    parser.add_argument('--tokenizer_name', type=str, default='bert-large-cased',
                        help='Name or path of the tokenizer/vocabulary')
    parser.add_argument('--output_file', type=str, required=True,
                        help='Output file')
    parser.add_argument('--raw_text', type=bool, default=False,
                        help='Should be set as true, if input is raw text.')
    return parser

if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()
    gen_connl()
    gen_jsonlines()