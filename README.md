# WhoSaidIt
## Multi voiced audio generator with quote attribution


This project is under development, corerference resolution part has been implemented and can be executed by running 

`` 
  cd coref_resolution &&
  python main.py --filepath ./data/{file_name} --output_dir ./data
``

quote attribution has also been implemeted, now the pipeline sequence of coreference resolution + quote attribution can be executed with

``
  python main.py --filepath ./data/{filepath} --output_dir ./out
``

Voice synthesis can be executed as 

``
  cd voice_synthesis &&
  python main.py --filepath ../out/quote_attr/{quotes filepath}--coref_path ../out/coref/{coref filepath}  --output_dir ./out/voice
``

----------
## References

The coreference resolution module has been heavily inspired from the paper "Incremental Neural Coreference Resolution in Constant Memory" by Xia, Patrick and his [repo]([https://](https://github.com/pitrack/incremental-coref)).

```
@inproceedings{xia-etal-2020-incremental,
    title = "Incremental Neural Coreference Resolution in Constant Memory",
    author = "Xia, Patrick  and
      Sedoc, Jo{\~a}o  and
      Van Durme, Benjamin",
    booktitle = "Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)",
    year = "2020",
    url = "https://aclanthology.org/2020.emnlp-main.695",
    doi = "10.18653/v1/2020.emnlp-main.695",
}
```

And the entire pipline for quote attribution has been inspired from [fanfiction-nlp]([https://](https://github.com/michaelmilleryoder/fanfiction-nlp))

> 

    Michael Miller Yoder, Sopan Khosla, Qinlan Shen, Aakanksha Naik, Huiming Jin, Hariharan Muralidharan, and Carolyn P Rosé. 2021. FanfictionNLP: A Text Processing Pipeline for Fanfiction. In Proceedings of the 3rd Workshop on Narrative Understanding, pages 13–23.

