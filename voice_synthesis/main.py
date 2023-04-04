import argparse
import os
import json
import numpy as np
import itertools

from nltk.tokenize.treebank import TreebankWordDetokenizer
detokenizer = TreebankWordDetokenizer()

try:
    from . import speaker_data
    from .gen_voices import gen_char_voice, gen_narr_voice, get_audio
except ImportError:
    import speaker_data
    from gen_voices import gen_char_voice, gen_narr_voice, get_audio


from itertools import islice
 
 
def chunk(arr_range, arr_size):
    arr_range = iter(arr_range)
    return iter(lambda: tuple(islice(arr_range, arr_size)), ())
 
 

class VoiceSynthesizer:
    def __init__(self, input_path, coref_path, output_dir, gen_voices_file) -> None:
          self.input_path = input_path
          self.output_dir = output_dir
          self.coref_path = coref_path
          self.gen_voice_files = gen_voices_file
          self.temp_dir = os.path.join(output_dir, "temp")
          self.quotes, self.speakers = self.process_input()
          

    def process_input(self):
        with open(self.input_path, "r") as f:
              buff = json.load(f)
        return buff['quotes'], buff['speakers']

    def gen_dialog(self, text, speaker, output=None):
        text = self.detok(text)
        return gen_char_voice(text.strip(), speaker, output)


    def gen_narration(self, text, output=None):
        text = self.detok(text)
        return gen_narr_voice(text.strip(), output)

    def sort_quotes(self):
        self.quotes = sorted(self.quotes, key=lambda x: x['position'])

    def load_coref(self):
        with open(self.coref_path, "r") as f:
            coref = json.load(f)
        return coref
    
    def detok(self, text):
        return detokenizer.detokenize(text)

    def run(self):
        self.sort_quotes()
        speakers = set([q['speaker_id'] for q in self.quotes])
        s_va_m = speaker_data.get_male_speakers(shuffle=True)
        s_va_f = speaker_data.get_female_speakers(shuffle=True)
        speakers = { s: s_va_m[i]['id'] if self.speakers[s]['gender']=="male" else s_va_f[i]['id'] for i,s in enumerate(speakers) }
        print(speakers)
        doc = self.load_coref()["document"].split()
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)


        prev=0
        res=[]
        c=0
        for quote in self.quotes:
            start = quote['position'][0]
            narration: list = doc[prev:start]
            # print(chunk(narration, 100))
            # break
            if(narration):
                # for nar in  chunk(narration, 100):
                    res+=self.gen_narration(narration, output=os.path.join(self.temp_dir, str(c)+"_narr.wav") if self.gen_voice_files else None)
                    print(c)
                    c+=1
            # for dia in  chunk(quote['text'].split(), 100):
            res+=self.gen_dialog(quote['text'].split(), speakers[quote['speaker_id']], output=os.path.join(self.temp_dir, str(c)+"_quote.wav") if self.gen_voice_files else None)
            print(c)
            c+=1
            prev=quote['position'][1]+1

        fname = os.path.splitext(os.path.basename(self.input_path))[0]

        get_audio(res, os.path.join(self.output_dir, fname+".wav"))


def get_args():
     parser = argparse.ArgumentParser()
     parser.add_argument('--filepath', type=str, required=True,
                    help='Path of input file')
     parser.add_argument('--coref_path', type=str, required=True,
                    help='Path of coreference output')
     parser.add_argument('--output_dir', type=str, required=True,
                    help='Output Dir')
     parser.add_argument('--gen_voice_files', type=lambda x: (str(x).lower() == 'true'), required=False,
                    default = False, help='Set True if you want to generate voice for each quote seperately.')
     return parser


if __name__ == "__main__":
     parser = get_args()
     args = parser.parse_args()
     voicer = VoiceSynthesizer(args.filepath, args.coref_path, args.output_dir, args.gen_voice_files)
     voicer.run()