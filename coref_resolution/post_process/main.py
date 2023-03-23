import argparse
import inference
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True,
                        help='Name of preds JSON file')
    parser.add_argument('--output_file', type=str, required=True,
                        help='Output file')
    return parser

def convert_preds_to_text(fpath, out_path):
    inference.main(fpath, out_path)
    pass

def postprocess(fpath, out_path):
    """
        Function that assigns a static names to each infered text cluster mentions.
    """
    pass

def main(fpath, infered_path, out_path):
    """
        Main function that performs post processing to convert the output of predictions generated from model into input format required for quote attribution.
    """

    convert_preds_to_text(fpath, infered_path)
    postprocess(infered_path, out_path)
    pass

if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()
    infered_path=os.path.join("temp", "infered.json")
    main(args.filename,infered_path, args.outfile, )