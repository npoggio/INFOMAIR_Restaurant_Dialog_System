from transformers import DistilBertTokenizer, DistilBertModel
from sklearn.feature_extraction.text import CountVectorizer
from typing import List

import numpy as np
import torch

tokenizer = DistilBertTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

model = DistilBertModel.from_pretrained(
    "distilbert-base-uncased"
)

# Do not use dropout while creating embeddings.
model.eval()


def get_distilbert_embeddings(
    count_vectorizer: CountVectorizer,
    texts: List[str],
) -> np.ndarray:
    """
    Creates frozen DistilBERT embeddings for a list of texts.

    `count_vectorizer` is not used, but is included so that this function
    can be used in exactly the same place as `get_embeddings` in the models created in model map.
    the only thing that needs to be copied at the top of the document is; from src.utils.distilbert_embeddings import get_distilbert_embeddings
    """
    if isinstance(texts, str):
        raise TypeError(
            "Argument `texts` must be an iterable of str objects, not a str object"
        )

    _ = count_vectorizer

    encoded_input = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )

    # DistilBERT remains frozen.
    with torch.no_grad():
        output = model(**encoded_input)

    # Take the first token representation as the utterance embedding.
    # Resulting shape: (number of texts, 768)
    embeddings = output.last_hidden_state[:, 0, :]

    return embeddings.numpy()