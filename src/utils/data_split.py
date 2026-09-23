# data_split.py

from dataclasses import dataclass

from sklearn.model_selection import train_test_split


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
    stratify: bool = True,     # split data across classes
) -> DataSplit:
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    stratify_labels = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_labels,
    )

    return DataSplit(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
    )