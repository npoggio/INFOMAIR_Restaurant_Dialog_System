from enum import StrEnum, auto


class Models(StrEnum):
    RULE_BASED = auto()
    SUPPORT_VECTOR_MACHINE_BOW = auto()
    LOGISTIC_REGRESSION_BOW = auto()
    SUPPORT_VECTOR_MACHINE_BERT = auto()
    RULE_BASED_BERT = auto()
    LOGISTIC_REGRESSION_BERT = auto()