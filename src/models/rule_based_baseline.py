import re

from sklearn.metrics import accuracy_score
from src.enums.dialog_act import DialogAct
from src.utils.parser import sanitize_phrase

from src.enums.dialog_act import DialogAct
from src.utils import parser
from src.utils.data_split import split_data
from src.utils.document_term import transpose_dialog_acts

DATA_PATH = "data/dailog_acts.dat"
RANDOM_STATE = 12345

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
    DialogAct.REQUALTS: (
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
    # Avoid circular import
    from src import DO_LOWER, REMOVE_APOSTRAPHES

    #text = utterance.lower().strip()
    text = sanitize_phrase(utterance, DO_LOWER, REMOVE_APOSTRAPHES)

    for dialog_act, keywords in RULES.items():
        for keyword in keywords:
            if contains_keyword(text, keyword):
                return dialog_act

    return DialogAct.NULL #Default

# if __name__ == "__main__":

    # while True:
        # utterance = input("Enter an utterance (or 'quit' to stop): ")

        # if utterance.lower().strip() == "quit":
            # break

        # prediction = classify_dialog_act(utterance)

        # print(f"Predicted dialog act: {prediction.value}")

def evaluate_rulebase():
    lines = parser.read_text_file_lines(DATA_PATH)
    dialog_acts = parser.parse_dstc_dat_file(lines)

    phrases, classes = transpose_dialog_acts(dialog_acts)

    data = split_data( 
        X=phrases,
        y=classes,
        test_size=0.15,
        random_state=RANDOM_STATE
    )

    predictions = []

    for utterance in data.X_test:
        prediction = classify_dialog_act(utterance)
        predictions.append(prediction)
    
    print(
        "Accuracy:",
        accuracy_score(data.y_test, predictions),
    )

if __name__ == "__main__":
    evaluate_rulebase()
