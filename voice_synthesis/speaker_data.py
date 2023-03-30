import pandas as pd
from random import sample
speaker_data = pd.read_csv("./speaker-gender.csv").to_dict("records")
females = [speaker for speaker in speaker_data if speaker['gender']=="female"]
males = [speaker for speaker in speaker_data if speaker['gender']=="male"]

def get_male_speakers(shuffle=False):
    if shuffle:
        return sample(males, len(males))
    return males
def get_female_speakers(shuffle=False):
    if shuffle:
        return sample(females, len(females))
    return females