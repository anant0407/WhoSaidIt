# import argparse
import os


from TTS.api import TTS

narr_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=True)

dialog_model = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=True)


def gen_char_voice(text, speaker, output=None):
     if output:
          wav = dialog_model.tts(text, speaker)
          dialog_model.synthesizer.save_wav(wav, output)
          return wav
     else: 
          return dialog_model.tts(text, speaker)
def gen_narr_voice(text, output=None):
     if output:
          wav = narr_model.tts(text)
          narr_model.synthesizer.save_wav(wav, output)
          return wav
     else:
          return narr_model.tts(text)
     
def get_audio(wav, file):
     narr_model.synthesizer.save_wav(wav, file)

# def speakers


# def get_args():
#      parser = argparse.ArgumentParser()
#      parser.add_argument('--quotes', type=str, required=True,
#                     help='Path of quotes.json file')
#      parser.add_argument('--output_dir', type=str, required=True,
#                     help='Output Dir')
#      return parser


if __name__ == "__main__":
    pass
     # parser = get_args()
     # args = parser.parse_args()