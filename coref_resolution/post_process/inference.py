import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True,
                        help='Name of preds JSON file')
    parser.add_argument('--output_file', type=str, required=True,
                        help='Output file')
    return parser

def main(fpath, out_path):
    """
        Main funtion that converts string indicies (start, end) to text.

        Output will be stored in out_path provided.
    """
    pass

if __name__ == "main":
    parser = get_args()
    args = parser.parse_args()
    main(args.filename, args.outfile)