import sys
import os
import spacy
import nltk

nlp = spacy.load('en')
def tokenize(text):
    return ' '.join([tok.text for tok in nlp.tokenizer(text)])

def get_text(fpath):
    with open(fpath, "r") as f:
        buff = f.readlines()
        buff = [tokenize(para) for para in buff]
    return buff

def convert(fpath, out_dir):
    fname = os.path.splitext(os.path.basename(fpath))[0]
    conll_output=[]
    count=0

    conll_output.append(['#begin document (' + str(fname) + '); part 0'])

    for p, tokens in enumerate(get_text(fpath)):
        para = "".join(tokens)
        sents = nltk.sent_tokenize(para)
        for sent in sents:
            for x, t in enumerate(sent.split()):
                i = x + count
                conll_output.append([str(fname), '0', str(x), str(t), "0", str(p), str(i+1), '-', '-', '-', '-', '-'])
            count += len(sent.split())
            conll_output.append([''])
        conll_output.append(['#end document'])
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    with open(out_dir + "/" + str(fname) + ".conll", "w") as f:
        for l in conll_output:
            f.write('\t'.join(l) + '\n')
    return True

if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("Insufficient args")
        exit()
    convert(sys.argv[1], sys.argv[2])

# python convert_to_txt_conll.py test.txt ./temp