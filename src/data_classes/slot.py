from dataclasses import dataclass

DONT_CARE: str = "dontcare"

@dataclass
class Slot:
    question: str
    value: str = ""

    @property
    def filled(self) -> bool:
        return self.value != ""
