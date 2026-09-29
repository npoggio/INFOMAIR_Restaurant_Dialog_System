from enum import StrEnum, auto


class DialogAct(StrEnum):
    ACK = auto()
    AFFIRM = auto()
    BYE = auto()
    CONFIRM = auto()
    DENY = auto()
    HELLO = auto()
    INFORM = auto()
    NEGATE = auto()
    NULL = auto()
    REPEAT = auto()
    REQUALTS = auto()
    REQMORE = auto()
    REQUEST = auto()
    RESTART = auto()
    THANKYOU = auto()