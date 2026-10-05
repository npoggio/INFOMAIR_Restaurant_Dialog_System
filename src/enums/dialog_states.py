from enum import StrEnum, auto

class DialogState(StrEnum):
    INTRODUCTION = auto()
    ASK_PREFERENCES = auto()
    CONFIRM = auto()
    SUGGEST = auto()
    GIVE_INFO = auto()
    END = auto()
