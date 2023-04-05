import argparse
import json
import csv
from ast import literal_eval
import pandas as pd
from nltk.tokenize.treebank import TreebankWordDetokenizer
from fuzzywuzzy import fuzz
import pickle


def processActuals(actual):
    actual_df = pd.read_csv(actual, converters={'qTextArr': literal_eval})
    actual_df = actual_df[['qTextArr', 'speaker']]
    buff = []
    for quotes,speaker in actual_df.values:
       for quote in quotes:
           buff.append({
               'quote': quote.replace('\n', ' ').strip(),
               'speaker': speaker
           })
    return buff

def processPreds(preds):
    detokenizer = TreebankWordDetokenizer()
    with open(preds) as f:
        buff = json.load(f)
        for quotes in buff['quotes']:
            quotes['text'] = detokenizer.detokenize(quotes['text'].strip().replace("\"", "").split())
            quotes['speaker_id'] = buff['speakers'][quotes['speaker_id']]['name']
    return buff['quotes']

def processChars(chars):
    with open(chars, "rb") as f:
        buff = pickle.load(f)
        # print(buff['id2names'])
        mens = {}
        for _id, alias in buff['id2names'].items():
            mens[list(buff['id2parent'][_id])[0]] = list(alias)

        # for _id in mens.keys():
        #     name = list(buff['id2parent'][_id])[0]
        #     mens[name] = mens.pop(_id)
    return (mens)


def getAccuracy(preds, actuals, chars):
    correct=0
    actuals_cnt=0
    i=0
    while i<len(preds):
        if(fuzz.partial_ratio(preds[i]['text'], actuals[actuals_cnt]['quote'])<60):
            print("Inconsistent quotes: MISMATCH!! : ", preds[i]['text'],"<--->", actuals[actuals_cnt]['quote'], fuzz.partial_ratio(preds[i]['text'], actuals[actuals_cnt]['quote']))
            # print(preds[i+1]['text'], actuals[actuals_cnt]['quote'], fuzz.partial_ratio(preds[i+1]['text'], actuals[actuals_cnt]['quote']))
            if(fuzz.partial_ratio(preds[i+1]['text'], actuals[actuals_cnt]['quote'])>80):
                i+=1
            elif(fuzz.partial_ratio(preds[i]['text'], actuals[actuals_cnt+1]['quote'])>80):
                actuals_cnt+=1
            else:
                print("Inconsistent")
                return correct/actuals_cnt
        try:
            speaker = chars[actuals[actuals_cnt]['speaker']]
        except:
            print(actuals[actuals_cnt]['speaker'])
            i+=1
            actuals_cnt+=1
            continue

        if (preds[i]['speaker_id'] in speaker):
            correct+=1
        elif (max([fuzz.partial_ratio(preds[i]['speaker_id'], x) for x in speaker]) > 80):
            correct+=1
        else:
            print(preds[i]['speaker_id'],"----", actuals[actuals_cnt]['speaker'])
        i+=1
        actuals_cnt+=1
    return correct/(actuals_cnt-1)
        

def run(preds, actuals, chars):
   actuals = processActuals(actuals)
   preds = processPreds(preds)
   chars = processChars(chars)
#    print(preds[123], actuals[123])
#    exit()
   print("Accuracy: ", getAccuracy(preds,actuals, chars))







def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preds', type=str, required=True,
                help='Path of input file')
    parser.add_argument('--actual', type=str, required=True,
                help='Actual')
    parser.add_argument('--chars', type=str, required=True,
                help='Chars')
    return parser


if __name__ == "__main__":
    parser = get_args()
    args = parser.parse_args()
    run(args.preds, args.actual, args.chars)
    

