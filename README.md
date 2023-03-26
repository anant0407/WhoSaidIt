# WhoSaidIt
## Multi voiced audio generator with quote attribution


This project is under development, corerference resolution part has been implemented and can be executed by running 

``` python coref_resolution/predict.py
```

**input data has to be put in coref_resolution/data/train.jsonlines**

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

