# data_split.py

from collections import Counter, defaultdict
from dataclasses import dataclass

import numpy as np
from sklearn.model_selection import train_test_split

MAX_SENTENCE_SHARE = 0.25


@dataclass
class DataSplit:
    X_train: list
    X_test: list
    y_train: list
    y_test: list


def split_data(
    X, # utterances
    y, # classes
    test_size: float = 0.15,   # test size
    random_state: int = 12345, # random seed
    grouped: bool = False,     # keep identical utterances in the same split
) -> DataSplit:
    """Splits the data into train and test, stratified by class."""
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    if grouped:
        return _grouped_split(X, y, test_size, random_state)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    return DataSplit(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
    )


def _grouped_split(X, y, test_size: float, random_state: int) -> DataSplit:
    """
    Splits the data so that every copy of a sentence ends up in the same split,
    so no sentence can appear in both the train and the test set.

    For each class, the test set is filled with whole sentences (all their copies at once)
    until that class has roughly `test_size` of its rows in the test set.
    Very frequent sentences (see `MAX_SENTENCE_SHARE`) always stay in train.
    """
    X = np.asarray(X, dtype=object)
    y = np.asarray(y, dtype=object)
    rng = np.random.default_rng(random_state)

    # Count how often each sentence appears, and how often with each class
    sentence_sizes = Counter(X)
    sentence_classes = defaultdict(Counter)
    for sentence, label in zip(X, y):
        sentence_classes[sentence][label] += 1

    # Give each sentence one class (its most common one) and put it in the list for that class
    # e.g. class_sentences["affirm"] = ["right", "yeah", "yes", ...]
    class_sentences = defaultdict(list)
    for sentence in sorted(sentence_classes):
        label = sentence_classes[sentence].most_common(1)[0][0]
        class_sentences[label].append(sentence)

    # For each class choose which of its sentences go into the test set
    test_sentences = set()
    for label in sorted(class_sentences):
        sentences = class_sentences[label]

        # How many rows of this class should end up in the test set (ex. 15%)
        n_rows = sum(sentence_sizes[s] for s in sentences)
        target = test_size * n_rows
        n_test = 0

        # Prevents sentences with very frequent copies from filling up the test set
        max_size = max(1, MAX_SENTENCE_SHARE * target)

        # Go through the sentences in random order
        for sentence in rng.permutation(sentences):
            size = sentence_sizes[sentence]  # How often this sentence appears
            if size > max_size:
                continue

            distance_now = abs(n_test - target)
            distance_if_added = abs(n_test + size - target)

            # Only add the sentence if it brings us closer to the target
            if distance_if_added < distance_now:
                test_sentences.add(sentence)
                n_test += size

    # Put every row in train or test, depending on its sentence
    X_train, X_test, y_train, y_test = [], [], [], []

    for sentence, label in zip(X, y):
        if sentence in test_sentences:     # this sentence was chosen for test
            X_test.append(sentence)
            y_test.append(label)
        else:                              # everything else goes to train
            X_train.append(sentence)
            y_train.append(label)

    return DataSplit(
        X_train=X_train, 
        X_test=X_test, 
        y_train=y_train, 
        y_test=y_test
    )

