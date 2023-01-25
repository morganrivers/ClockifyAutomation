from spacy.training import Example

import en_core_web_sm
import pandas as pd

import re


def clean_data(raw_events):
    """
    this function will iterate through the raw_events string and remove the 'app' and
    'title' tags and other symbols
    """
    raw_events_after_data = [x.split("data")[1] for x in raw_events]

    cleaned_events = []
    for event in raw_events_after_data:
        cleaned = re.sub(r"[^\w]", " ", event).replace("title", "").replace("app", "")
        print("")
        print("cleaned")
        print(cleaned)
        cleaned_events.append(cleaned)

    return cleaned_events


def import_data_for_training():
    """
    return labelled data for the purposes of training the text categorizer model
    """
    window_titles = pd.read_csv(
        "test_data/training_data.csv", delimiter=";", decimal=","
    )

    cleaned_events = clean_data(window_titles["events"].values)

    train_labels = [
        {
            "cats": {
                "programming": label == "p",
                "browsing": label == "b",
                "email": label == "e",
                "miscellaneous": label == "m",
            }
        }
        for label in window_titles["label"]
    ]

    train_data = list(zip(cleaned_events, train_labels))

    return train_data


# def print_model_predictions(nlp, test_text):
#     """
#     test the trained model, by printing the likelihood that the test_text argument is
#     in the category for each category
#     """
#     doc = nlp(test_text)
#     # test the trained model before resizing
#     # test_text = "I am happy."
#     doc = nlp(test_text)
#     assert len(doc.cats) == 2
#     pos_pred = doc.cats["POSITIVE"]
#     neg_pred = doc.cats["NEGATIVE"]
#     print("pos_pred")
#     print(pos_pred)
#     print("neg_pred")
#     print(neg_pred)


def print_model_predictions(nlp, test_text):
    """
    test the trained model, by printing the likelihood that the test_text argument is
    in the category for each category
    """
    doc = nlp(test_text)

    programming_pred = doc.cats["programming"]
    browsing_pred = doc.cats["browsing"]
    email_pred = doc.cats["email"]
    miscellaneous_pred = doc.cats["miscellaneous"]

    print("list of predictions")
    print(
        {
            "programming": programming_pred,
            "browsing": browsing_pred,
            "email": email_pred,
            "miscellaneous": miscellaneous_pred,
        }
    )


def create_trained_model(train_data_single_label):
    """
    initialize the model for text categorization, train it, and return the model
    """

    nlp = en_core_web_sm.load()

    nlp.add_pipe("textcat")

    # make a list of Example objects using the text and annotations
    train_examples = []
    for text, annotations in train_data_single_label:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))

    # initialize the language model optimizer with the examples
    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    # train the model
    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
        print("losses")
        print(losses)

    return nlp


# # # MAIN # # #

# train_data_single_label = [
#     ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
#     ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
#     ("The dog is sad", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
# ]

train_data_single_label = import_data_for_training()
nlp = create_trained_model(train_data_single_label)
# print_model_predictions_simple(nlp, "I am happy!")
# print_model_predictions_simple(nlp, "The dog is angry")
print_model_predictions(
    nlp,
    "': {'app': 'Firefox-esr', 'title': 'Inbox (4,632) - danielmorganrivers@gmail.com - Gmail — Mozilla Firefox'}}",
)
