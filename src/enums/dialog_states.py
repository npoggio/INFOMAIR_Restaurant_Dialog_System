from enum import StrEnum, auto

class DialogState(StrEnum):
    INTRODUCTION = auto()
    ASK_PREFERENCES = auto()
    CONFIRM_SLOT = auto()
    INFORM = auto()
    CONFIRM = auto()
    SUGGEST = auto()
    GIVE_INFO = auto()
    END = auto()
