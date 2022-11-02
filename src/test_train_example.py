from spacy.lang.en import English
from spacy.tokens import Doc, DocBin
from spacy.training import Alignment, Corpus, Example, biluo_tags_to_offsets
from spacy.training import biluo_tags_to_spans, docs_to_json, iob_to_biluo
from spacy.training import offsets_to_biluo_tags
from spacy.training.alignment_array import AlignmentArray
from spacy.training.align import get_alignments
from spacy.training.converters import json_to_docs
from spacy.util import get_words_and_spaces, load_model_from_path, minibatch
from spacy.util import load_config_from_str
from thinc.api import compounding


TRAIN_DATA_SINGLE_LABEL = [
    ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
]

def make_get_examples_single_label(nlp):
    train_examples = []
    for t in TRAIN_DATA_SINGLE_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    def get_examples():
        return train_examples

    return get_examples

def test_issue9904():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples_single_label(nlp)
    nlp.initialize(get_examples)

    examples = get_examples()
    scores = textcat.predict([eg.predicted for eg in examples])

    loss = textcat.get_loss(examples, scores)[0]
    loss_double_bs = textcat.get_loss(examples * 2, scores.repeat(2, axis=0))[0]
    assert loss == pytest.approx(loss_double_bs)

def test_simple_train():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    textcat.add_label("answer")
    nlp.initialize()
    for i in range(5):
        for text, answer in [
            ("aaaa", 1.0),
            ("bbbb", 0),
            ("aa", 1.0),
            ("bbbbbbbbb", 0.0),
            ("aaaaaa", 1),
        ]:
            nlp.update((text, {"cats": {"answer": answer}}))
    doc = nlp("aaa")
    assert "answer" in doc.cats
    assert doc.cats["answer"] >= 0.5

