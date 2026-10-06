from typing import Dict, Any, List, Tuple
import argparse
import sys
from src.enums.dialog_act import DialogAct
#from src.enums.info_request_type import InfoRequestType
from src.run import run_str
from src.enums.models import Models
from src.enums.dialog_states import DialogState
import src.enums.restaurant_props as rpe
from src import PROGRAM, DESCRIPTION, MODEL_NAMES
import src.utils.parser as upar
from dataclasses import dataclass

ALLOWED_MODELS = list(MODEL_NAMES.keys())

#TEMP TODO: load this in on first instance
file_path: str = 'data/restaurant_info_extended.csv'
rest_data = upar.load_restaurant_data(file_path)


@dataclass
class Slot:
    question: str
    value: str = ""

    @property
    def filled(self) -> bool:
        return self.value != ""

slots: Dict[rpe.StrEnum, Slot] = {
    rpe.Food:        Slot(question="What kind of food would you like?"),
    rpe.Area:        Slot(question="What part of town do you have in mind?"),
    rpe.PriceRange:  Slot(question="Would you like something cheap, moderate or expensive?"),
}

# Restaurants matching the current preferences, and which one we are currently suggesting.
possible_restaurants: List[str] = []
restaurant_index: int = 0

def dialog_arg_parser() -> Dict[str, Any]:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIPTION,
    )

    # Model
    parser.add_argument('-m', '--model',
                        type=str, required=True, help='Model types', choices=ALLOWED_MODELS)

    args = sys.argv[1:]
    namesp = parser.parse_args(args=args)
    return namesp.__dict__


def state_transition(state: DialogState, dialog_act: DialogAct, utterance: str) -> Tuple[DialogState, str]:
    # Repeatedly introduce and ask for user input until ther user provides us with more information.
    if state == DialogState.INTRODUCTION:
        if dialog_act == DialogAct.INFORM or extract_preferences(utterance):
            return handle_inform(utterance)
        if dialog_act == DialogAct.HELLO:
            return DialogState.INTRODUCTION, get_intro_sentence()
        if dialog_act == DialogAct.BYE:
            return DialogState.END, "Goodbye!"
        return DialogState.INTRODUCTION, get_repromt_for_missing_slots()

    if state == DialogState.ASK_PREFERENCES:
        if dialog_act == DialogAct.INFORM:
            return handle_inform(utterance)
        else:
            return DialogState.ASK_PREFERENCES, get_repromt_for_missing_slots()

    if state == DialogState.INFORM:
        if dialog_act == DialogAct.CONFIRM or dialog_act == DialogAct.AFFIRM: # TODO: which one is correct? or both
            return DialogState.CONFIRM, "Great! I'll reserve that for you."
        if dialog_act == DialogAct.DENY or dialog_act == DialogAct.NEGATE:
            return DialogState.INFORM, offer_restaurant_suggestion(next_restaurant=True)
        if dialog_act == DialogAct.REQUEST:
            return DialogState.INFORM, get_restaurant_details()
        if dialog_act == DialogAct.RESTART:
            return DialogState.INTRODUCTION, get_intro_sentence()
    

    # This is basically hit anytime once the user has confirmed or thank you. TODO: probably bugs with this. needs testing    
    return DialogState.END, "We'll pick a restaurant for you! Coming soon in theaters :)"

#TODO: how to deal with dont care responses? ex. what kind of food do you want? i dont care
#TODO: how to handle negating responses? ex. what kind of food do you want? i dont want chinese
def handle_inform(utterance: str) -> Tuple[DialogState, str]:
    """Stores every preference extracted from the utterance, overwriting any value that was already stored.
    Then asks for the next missing preference, or suggests a restaurant once all are known."""
    new_preferences = extract_preferences(utterance)
    for info_request_type, info_request_value in new_preferences.items():
        slots[info_request_type].value = info_request_value

    if not new_preferences:
        return DialogState.ASK_PREFERENCES, get_repromt_for_missing_slots()

    # Ask for the first preference we don't know yet.
    missing_slot = next_missing_slot()
    if missing_slot:
        # LATER: repeat the new preferences back to the user before asking the next question. Only do this if they swithc their mind?
        # return DialogState.ASK_PREFERENCES, "You said you wanted " + describe_restaurant(new_preferences) + ". " + missing_slot.question
        return DialogState.ASK_PREFERENCES, missing_slot.question

    # All preferences are known, so suggest a restaurant and let the user confirm it.
    return DialogState.INFORM, offer_restaurant_suggestion()

def offer_restaurant_suggestion(next_restaurant: bool = False) -> str:
    global possible_restaurants, restaurant_index

    preferences = {}
    for info_request_type, slot in slots.items():
        preferences[info_request_type] = slot.value

    if next_restaurant:
        restaurant_index += 1
    else:
        possible_restaurants = find_restaurants(preferences)
        restaurant_index = 0

    if restaurant_index >= len(possible_restaurants):
        return "Sorry, there are no more restaurants that are " + describe_restaurant(preferences) + "."
    return possible_restaurants[restaurant_index] + " is " + describe_restaurant(preferences) + ". Does that sound good?" # TODO: dont use the users preferences to descirbe the restuarant. use the actual restaurant attributes

def find_restaurants(preferences: Dict[rpe.StrEnum, str]) -> List[str]:
    #return ["McDonald's", "Burger King"]  # TODO: use Jesse's restaurant finder
    pref_ = {k.__name__.lower(): v for k, v in preferences.items()}
    rests = upar.fetch_resturant_by_info(rest_data, **pref_)
    print(rests)
    return [r.title() for r in rests['restaurantname'].to_list()]

def get_restaurant_details() -> str:
    #details = possible_restaurants[restaurant_index].details TODO: wait for Jesse to implement this
    return "Phone number is 123-456-7890. Address is 123 Main St." 

def next_missing_slot() -> Slot:
    for slot in slots.values():
        if not slot.filled:
            return slot
    return None

def get_intro_sentence() -> str:
    return "Hello, welcome to super cool restaurant recommendation system! You can ask for restaurants by area, price range or food type. How may I help you?\nType QUIT to exit"

def get_repromt_for_missing_slots() -> str:
    missing_slot = next_missing_slot()
    if missing_slot:
        return "Sorry I didn't catch that. " + missing_slot.question
    return "Sorry, I didn't understand. Could you please rephrase?"

def describe_restaurant(preferences: Dict[rpe.StrEnum, str]) -> str:
    """Turns {PRICE_RANGE: "moderate", FOOD_TYPE: "french", AREA: "east"} into
    'a moderately priced French restaurant in the east of town'."""
    words = []

    price_range = preferences.get(rpe.PriceRange)
    if price_range:
        words.append("moderately priced" if price_range == "moderate" else price_range)

    food_type = preferences.get(rpe.Food)
    if food_type:
        words.append(food_type.title())

    words.append("restaurant")
    description = " ".join(words)
    description = ("an " if description[0].lower() in "aeiou" else "a ") + description

    area = preferences.get(rpe.Area)
    if area:
        description += f" in the {area} of town"

    return description

# TEMPORARY: keyword lists for testing until the real slot extraction is implemented.
#TEMP_KEYWORDS: Dict[InfoRequestType, List[str]] = {
#    InfoRequestType.AREA:        ["north", "south", "east", "west", "centre"],
#    InfoRequestType.PRICE_RANGE: ["cheap", "moderate", "expensive"],
#    InfoRequestType.FOOD_TYPE:   ["italian", "chinese", "indian", "thai", "french", "british", "spanish", "japanese", "korean", "mexican"],
#}

TEMP_KEYWORDS: Tuple = [rpe.Area, rpe.PriceRange, rpe.Food]


def extract_preferences(utterance: str) -> Dict[rpe.StrEnum, str]:
    # TEMPORARY: extract preferences from the utterance once madrie finishes slot extaction.
    words = utterance.lower().split()
    preferences = {}
    #for info_request_type, keywords in TEMP_KEYWORDS.items():
    #    for keyword in keywords:
    for rest_enum in TEMP_KEYWORDS:
        for keyword in rest_enum:
            if keyword in words:
                preferences[rest_enum] = keyword
    return preferences


def classify(model: Models, input_path: str, utterance: str) -> str:
    return DialogAct(run_str(model=model, input_path=input_path, phrases=[utterance])[0])


if __name__ == '__main__':
    kwargs = dialog_arg_parser()

    model_name = kwargs['model']
    input_path = f'model_files/{model_name}.joblib'

    model = MODEL_NAMES[model_name]

    print(get_intro_sentence())
    state = DialogState.INTRODUCTION

    while True:
        user_input = input("You: ")

        if user_input == 'QUIT':
            break

        dialog_act = classify(model, input_path, user_input)
        state, system_utterance = state_transition(state, dialog_act, user_input)
        print(f'System: {system_utterance}')

        if state == DialogState.END:
            break
