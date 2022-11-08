from spacy.lang.en import English
from spacy.training import Example

import en_core_web_sm


def test_trained_model(nlp):
    """
    test the trained model, by printing the prediction for each label on a new input
    """
    test_text = "I am happy."
    doc = nlp(test_text)
    assert len(doc.cats) == 2
    pos_pred = doc.cats["POSITIVE"]
    neg_pred = doc.cats["NEGATIVE"]
    print("pos_pred")
    print(pos_pred)
    print("neg_pred")
    print(neg_pred)


def create_trained_model(train_data_single_label):
    """
    initialize the model for text categorization, train it, and return the model
    """
    nlp = English()

    name = "textcat"

    nlp = en_core_web_sm.load()

    textcat = nlp.add_pipe(name)

    train_examples = []
    for text, annotations in train_data_single_label:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))

    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    # not really sure what this does...
    assert textcat.model.maybe_get_dim("nO") in [2, None]

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    return nlp


# # # MAIN # # #

train_data_single_label = [
    ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
]

nlp = create_trained_model(train_data_single_label)
test_trained_model(nlp)
