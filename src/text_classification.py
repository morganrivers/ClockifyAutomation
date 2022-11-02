import en_core_web_sm
import pandas as pd
import spacy
from spacy.pipeline.textcat_multilabel import DEFAULT_MULTI_TEXTCAT_MODEL
from spacy.training import Example
from spacy.util import minibatch, compounding


window_titles = pd.read_csv('test_data/training_data.csv', delimiter=";", decimal=",")

nlp = en_core_web_sm.load() 

config = {
   "threshold": 0.5,
   "model": DEFAULT_MULTI_TEXTCAT_MODEL,
}

nlp.add_pipe("textcat_multilabel", config=config)
textcat_multilabel = nlp.get_pipe('textcat_multilabel')

textcat_multilabel.add_label("programming")
textcat_multilabel.add_label("browsing")
textcat_multilabel.add_label("email")
textcat_multilabel.add_label("miscellaneous")

train_texts = window_titles['events'].values
train_labels = [{'cats': {'programming': label == 'p',
                          'browsing': label == 'b', 
                          'email': label == 'e', 
                          'miscellaneous': label == 'm'}}
                for label in window_titles['label']]

train_data = list(zip(train_texts, train_labels))

optimizer = nlp.initialize()
losses = {}

# TODO: what's minibatch doing
batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
for batch in batches:
    texts, annotations = zip(*batch)

example = []
# Update the model with iterating each text
for i in range(len(texts)):
    doc = nlp.make_doc(texts[i])
    example.append(Example.from_dict(doc, annotations[i]))

    nlp.update(
        example,
        drop=0.2,  # dropout - make it harder to memorise data
        sgd=optimizer,  # callable to update weights
        losses=losses
    )

# TODO: once we have the losses what do we want to use them for
print("Losses", losses)

# TODO: get the actual predictions
# run it on new data
# we use the updated model here with new data
doc = nlp(text)
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
# nlp.to_disk("./ncku_model")
# https://github.com/QiongyunChang/Chatbot_NLP/blob/29bb6462557ad79fbfe0f58b7dc0f5c598bd2dce/lab3/HW3_3.py