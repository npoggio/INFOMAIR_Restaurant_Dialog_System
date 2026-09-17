import re

from .utils.dialog_act import DialogAct


RULES = {
    DialogAct.BYE: ("see you", "goodbye", "good bye", "bye"),
    DialogAct.HELLO: ("hi", "hello", "good morning", "good evening"),
    DialogAct.DENY: ("wrong", "no", "not", "don't", "change"),
    DialogAct.AFFIRM: ("yes", "right", "yeah", "yea", "correct"),
    DialogAct.CONFIRM: ("is it", "does it", "what is", "do they"),
    DialogAct.ACK: ("okay", "good", "kay", "that'll do", "fine", "ok"),
    DialogAct.INFORM: (
        "looking",
        "need",
        "any",
        "restaurant",
        "north",
        "west",
        "east",
        "south",
        "food",
        "italian",
        "chinese",
        "indian", # TODO: get a more expansive list of cuisine types
        "expensive",
        "cheap",
        "price",
        "priced",
        "care",
        "serve",
        "kosher",
        "vegetarian",
        "vegan",
        "seafood",
    ),
    #TODO: Add more rules for the remaining dialog acts
}

def contains_keyword(text: str, keyword: str) -> bool:
    pattern = rf"\b{re.escape(keyword)}\b"
    return re.search(pattern, text) is not None


def classify_dialog_act(utterance: str) -> DialogAct:
    text = utterance.lower().strip()

    for dialog_act, keywords in RULES.items():
        for keyword in keywords:
            if contains_keyword(text, keyword):
                return dialog_act

    return DialogAct.NULL #Default

if __name__ == "__main__":
    while True:
        utterance = input("Enter an utterance (or 'quit' to stop): ")

        if utterance.lower().strip() == "quit":
            break

        prediction = classify_dialog_act(utterance)

        print(f"Predicted dialog act: {prediction.value}")