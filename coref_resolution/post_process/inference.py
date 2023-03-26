import argparse
import json
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True,
                        help='Name of preds JSON file')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Output directory')
    return parser

def main(fpath, out_path):
    """
        Main funtion that converts string indicies (start, end) to text.

        Output will be stored in out_path provided.
    """
    data = []
    
    with open(fpath, "r") as f:
        for l in f.readlines():
            data.append(json.loads(l.strip()))
    
    for d in data:
        doc_key= d['doc_key'][:-2]
        clusters = []

        for c, clus in enumerate(d['predicted_clusters']):
            cluster = {}
            cluster['mentions'] = []
            names = []
            # Change output from subtoken indices to full token indices
            for e, ele in enumerate(clus):
                tok_beg = d['subtoken_map'][ele[0]]
                tok_end = d['subtoken_map'][ele[1]] + 1
                phrase = ' '.join(d['tokens'][tok_beg:tok_end])
                cluster['mentions'].append({
                    'position': (tok_beg, tok_end),
                    'text': phrase})
                names.append(phrase)
            # Assign cluster canonical character name
            #cluster['name'] = canonical_character_name(Counter(names))
            clusters.append(cluster)
        output = {
            "document": " ".join(d['tokens']),
            "clusters":clusters,
        }
        fname = os.path.splitext(os.path.basename(fpath))[0]

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        with open(os.path.join(out_path, fname + ".json"), "w") as f:
            json.dump(output, f)

    pass

if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()
    main(args.filename, args.output_dir)