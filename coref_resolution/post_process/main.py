import argparse
from . import inference
import os
import json
import benepar, spacy
from collections import Counter
from nltk.corpus import wordnet
from nltk import Tree
from nltk.tag import StanfordNERTagger as NERTagger

from nltk.tokenize import word_tokenize

nlp_spacy = spacy.load('en_core_web_sm')
if spacy.__version__.startswith('2'):
    nlp_spacy.add_pipe(benepar.BeneparComponent("benepar_en3"))
else:
    nlp_spacy.add_pipe("benepar", config={"model": "benepar_en3"})


import inflect
p = inflect.engine()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str, required=True,
                        help='Name of preds JSON file')
    parser.add_argument('--infered_dir', type=str, required=True, 
                        help='Infered Directory')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Output directory')
    
    return parser

def convert_preds_to_text(fpath, out_path):
    inference.main(fpath, out_path)
    pass

def find_noun_phrases(tree):
    return [subtree for subtree in tree.subtrees(lambda t: t.label()=='NP')]

def find_head_of_np(np):
    noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
    top_level_trees = [np[i] for i in range(len(np)) if type(np[i]) is Tree]
    ## search for a top-level noun
    top_level_nouns = [t for t in top_level_trees if t.label() in noun_tags]
    if len(top_level_nouns) > 0:
        ## if you find some, pick the rightmost one, just 'cause
        return top_level_nouns[-1][0]
    else:
        ## search for a top-level np
        top_level_nps = [t for t in top_level_trees if t.label()=='NP']
        if len(top_level_nps) > 0:
            ## if you find some, pick the head of the rightmost one, just 'cause
            return find_head_of_np(top_level_nps[-1])
        else:
            ## search for any noun
            nouns = [p[0] for p in np.pos() if p[1] in noun_tags]
            if len(nouns) > 0:
                ## if you find some, pick the rightmost one, just 'cause
                return nouns[-1]
            else:
                ## return the rightmost word, just 'cause
                return np.leaves()[-1]


def canonical_character_name(names):
    """ Returns a chosen canonical character name.
        This is simply the most frequent capitalized variant
        that is not a stopword.
        Args:
            names: a Counter of name variants
    """

    if len(names) == 1:
        return list(names.keys())[0]

    # Remove stopwords
    # Choose most frequent name that has a capital letter
    processed_names = Counter()
    stops = ['he', 'him', 'his', 'himself',
             'she', 'her', 'hers', 'herself',
             'they', 'them', 'their', 'theirs',
             'i', 'me', 'my', 'mine',
             'we', 'us', 'our', 'ours',
             'you', 'your', 'yours', 'yourself',
            'mr.', 'mr', 'ms', 'ms.', 'miss', 'miss.', 'mrs', 'mrs.',
            'sir', "it", "its"
            ]
    for name, count in names.items():
        if name.lower() not in stops:
            processed_names[name] = count
    if len(processed_names) == 0:
        processed_names = names

    capitalized = Counter({
            name: count for name, count in processed_names.items() \
            if any(letter.isupper() for letter in name)})
    if len(capitalized) == 0:
        capitalized = processed_names

    return capitalized.most_common(1)[0][0]

def is_head_a_person_wordnet(name):

    # Reference: https://github.com/nikitakit/self-attentive-parser

    doc = nlp_spacy(name)
    sent = list(doc.sents)[0]
#     print(sent._.parse_string)

    from nltk import Tree

    tree = Tree.fromstring(sent._.parse_string)
    for np in find_noun_phrases(tree):
#         print("noun phrase:")
#         print(" ".join(np.leaves()))
        if " ".join(np.leaves()).lower() == name:
            head = find_head_of_np(np)
#             print("head:")
#             print(head)
            name = head
            break

#     print(name)

    # Reference: https://subscription.packtpub.com/book/application_development/9781782167853/1/ch01lvl1sec14/looking-up-synsets-for-a-word-in-wordnet

    syns = wordnet.synsets(name)
    if len(syns) > 0:
        syn = syns[0]
    else:
        return False
#     print(syn.hypernym_paths()[0])
    return len([s.name() for s in syn.hypernym_paths()[0] if "person" in s.name()]) > 0


def get_sentence_from_mention_pos(sents,pos):
    tok_cnt=0
    for sen_id, sen in enumerate(sents):
        if pos < tok_cnt:
            return sen_id-1
        tok_cnt+=len(sen.split())
    pass

def is_person_name_ner(data, pos, name):
    sen_id = get_sentence_from_mention_pos(data['sentences'], pos[0])
    sent = data['sentences'][sen_id]
    st = NERTagger('stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
    # print(data['document'].split()[pos[0]: pos[1]],pos[0], sent, name)
    
    tokens = word_tokenize(sent)
    # print(tokens)
    tags = st.tag(tokens)
    for tag in tags:
        if (tag[0] in name):
            # print("match")
            if (tag[1]=="PERSON"):
                # print(tag[0])
                return True

    return False
    
        
    # print(tags)


def postprocess(data):
    """
        Function that assigns a static names to each infered text cluster mentions.
    """
    men_to_pred = {tuple(m['position']): c for c, clus in enumerate(data['clusters']) for m in clus['mentions']}
    #mentions = sorted([tuple(m) for c, clus in enumerate(data['gold_clusters']) for m in clus])

    PRPs = ["it", "this", "that", "they", "them", "we", "these", "those", "our", "ours", "their", "theirs", "there", "its", "here"]

    plurals = ["they", "them", "we", "these", "those", "our", "their", 'people', 'parents']

    remove_PRPs = ["you", "me", "he", "she", "my", "mine", "your", "her", "his", "female", "male"]

    removable_mens = []
    out = {'document': data['document'],
            'clusters': []}

    # Remove any PRP mentions
    for i, clus in enumerate(data['clusters']):
        cluster = {'mentions': []}
        for j, men in enumerate(clus['mentions']):
            if not men['text'] in PRPs:
                cluster['mentions'].append(men)
        if len(cluster['mentions']) > 0:
            out['clusters'].append(cluster)
    clusters = []
    for clus in out['clusters']:
        mentions = [m['text'] for m in clus['mentions']]
        mentions_pos = [m['position'] for m in clus['mentions']]
        name = canonical_character_name(Counter(mentions))
        if (name.lower() == name) and (name.lower() not in remove_PRPs):
            if (p.singular_noun(name) is not False and name != p.singular_noun(name)):
                continue
            elif (not is_head_a_person_wordnet(name)):
                continue
        elif (not is_person_name_ner(data, mentions_pos[mentions.index(name)], name)): # there seems to be a problem between indexing of sentence and subtokens
            continue
        clus['name'] = name
        clusters.append(clus)
    out['clusters'] = clusters
    return out
    
    

def run(fpath, infered_path, out_path):
    """
        Main function that performs post processing to convert the output of predictions generated from model into input format required for quote attribution.
    """

    convert_preds_to_text(fpath, infered_path)
    model_out_file = os.path.splitext(os.path.basename(fpath))[0]
    
    buff = os.path.join(infered_path, model_out_file) + '.json'

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    if os.path.exists(buff):
        with open(buff, "r") as f:
            data = json.load(f)
    

        data = postprocess(data)
        
        with open(os.path.join(out_path, model_out_file + ".json"), 'w') as f:
            json.dump(data, f)
        print("post process successful. Output saved in", os.path.join(out_path, model_out_file + ".json" ))
    

if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()
    run(args.filename, args.infered_dir, args.output_dir,)