from dataclasses import dataclass


@dataclass
class DataSplit:
    X_train: list
    X_test: list
    y_train: list
    y_test: list
