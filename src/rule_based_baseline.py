import re

from utils.dialog_act import DialogAct

#TODO: get a more expansive list of cuisine types
CUISINES = (
    "italian",
    "chinese",
    "indian",
    "mexican",
    "vietnamese",
    "thai",
    "japanese",
    "korean",
    "spanish",
    "british",
    "greek",
    "turkish",
    "mediterranean",
    "scottish",
    "european",
    "hindi",
    "asian",
    "english"
)

RULES = {
    DialogAct.RESTART: (
        "restart",
        "start over",
        "start again",
        "reset"
    ),
    DialogAct.REQALTS: (
        "how about", 
        "next", 
        "anything else", 
        "different", 
        "what else", 
        "other", 
        "another", 
        "what about"
    ),
    DialogAct.THANKYOU: (
        "thank you",
        "thank"
    ),
    DialogAct.DENY: (
        "wrong",  
        "i dont want", 
        "change"
    ),
    DialogAct.NEGATE: (
        "no", #TODO decide whats the smartest thing to do with 'dont' and 'not' (also in other categories)
        "not"
    ), 
    DialogAct.REPEAT: (
        "repeat", 
        "again", 
        "back"
    ),
     DialogAct.REQUEST: (
        "what is", 
        "address", 
        "phone number", 
        "price range", 
        "post code", 
        "type (of food)", #TODO decide how to formulate this 
    ),
     DialogAct.CONFIRM: (
        "is it", 
        "does it",
        "do they"
    ),
    DialogAct.REQMORE: (
        "more"
    ),
    DialogAct.AFFIRM: (
        "yes", 
        "right", 
        "yeah", 
        "yea", 
        "correct"
    ),
    DialogAct.ACK: (
        "okay", 
        "good", 
        "kay", 
        "thatll do", 
        "fine", 
        "ok"
    ),
    DialogAct.HELLO: (
        "hi", 
        "hello", 
        "good morning", 
        "good evening"
    ),
    DialogAct.BYE: (
        "see you", 
        "goodbye", 
        "good bye", 
        "bye"
    ),
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
        "expensive",
        "cheap",
        "price",
        "priced",
        "care",
        "serve",
        "serves",
        "serving",
        "kosher",
        "vegetarian",
        "vegan",
        "seafood",
        "town",
        "center",
        "i dont care",
        "gastropub"
    ) + CUISINES,

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