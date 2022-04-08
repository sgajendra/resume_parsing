# -*- coding: utf-8 -*-
"""Resume parsing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/194diHTIx31MdhPP7mzbNhBoUOIn0hMRf
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import spacy
import warnings
from spacy.util import minibatch, compounding

import pickle

train_data = pickle.load(open('train_data.pkl','rb'))

train_data[0][0]

train_data[0][1].get("entities")[0][2]

##To train completely new entity:

nlp = spacy.blank('en')

def train_model(train_data):
    if 'ner' in nlp.pipe_names:
        ner = nlp.get_pipe("ner")
    else:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last='True')
    
    #------------------------------------
    # add labels
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("once", category=UserWarning, module='spacy')

        # reset and initialize the weights randomly – but only if we're
        # training a new model
        optimizer = nlp.begin_training()
            
        for itn in range(30):
            print(f"iteration {itn}.")
            random.shuffle(train_data)
            losses = {}
            for texts, annotations in train_data:
                try:
                    nlp.update(
                        [texts],  # batch of texts
                        [annotations],  # batch of annotations
                        drop=0.2,  # dropout - make it harder to memorise data
                        sgd = optimizer,
                        losses=losses,
                        )
                    print("Losses", losses) 
                except Exception as e:
                    pass

train_model(train_data)

nlp.to_disk('nlp_model')

##Testing of the model:
nlp = spacy.load('nlp_model')
test_text = train_data[0][0]
doc = nlp(test_text)
print("Entities in '%s'" % test_text)
for ent in doc.ents:
  print(f"{ent.label_:{30}} - {ent.text}")

nlp = spacy.load('nlp_model')
test_text = train_data[1][0]
doc = nlp(test_text)
print("Entities in '%s'" % test_text)
for ent in doc.ents:
  print(f"{ent.label_:{30}} - {ent.text}")

