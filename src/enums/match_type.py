from enum import StrEnum, auto

class MatchType(StrEnum):
    LEVENSHTEIN = auto()
    SEMANTIC_EMBEDDINGS = auto()