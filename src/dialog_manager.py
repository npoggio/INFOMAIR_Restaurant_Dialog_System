from typing import Dict, Any, List, Tuple
import argparse
import sys
import threading
from src.dialog.slot_extraction import extract_slots_keyword, extract_slots_semantic, get_word_with_levenshtein_distance, is_dont_care
from src.enums.dialog_act import DialogAct
#from src.enums.info_request_type import InfoRequestType
from src.enums.match_type import MatchType
from src.enums.restaurant_props import RestaurantInfoType
from src.run import run_str
from src.enums.models import Models
from src.enums.dialog_states import DialogState
import src.enums.restaurant_props as rpe
from src import PROGRAM, DESCRIPTION, MODEL_NAMES, MODEL_NAMES_DIALOG
from src.utils import tts
import src.utils.parser as parser
from src.data_classes.slot import Slot, DONT_CARE

ALLOWED_MODELS = list(MODEL_NAMES_DIALOG.keys())
INTO_SENTENCE: str = "Hello, welcome to super cool restaurant recommendation system! You can ask for restaurants by area, price range or food type. How may I help you?"
INTRO_PROMPT: str = "\nType QUIT to exit"  # Will never be read by TTS
intro_agg: str = INTO_SENTENCE + INTRO_PROMPT

LEVENSHTEIN_MAX_DISTANCE: int = 2
LEVENSHTEIN_MIN_WORD_LENGTH: int = 4

#TEMP TODO: load this in on first instance
file_path: str = 'data/restaurant_info_extended.csv'
rest_data = parser.load_restaurant_data(file_path)

slots: Dict[rpe.StrEnum, Slot] = {
    rpe.Food:        Slot(question="What kind of food would you like?"),
    rpe.Area:        Slot(question="What part of town do you have in mind?"),
    rpe.PriceRange:  Slot(question="Would you like something cheap, moderate or expensive?"),
}
pending_confirmations: Dict[rpe.StrEnum, str] = {}

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
    parser.add_argument('--tts', action='store_true',)
    parser.add_argument('--simllm', action='store_true')
    parser.add_argument('--match_type', type=MatchType, choices=list(MatchType), default=None,
                        help='Fallback slot matching when keyword matching fails')

    args = sys.argv[1:]
    namesp = parser.parse_args(args=args)
    return namesp.__dict__


def state_transition(state: DialogState, dialog_act: DialogAct, utterance: str) -> Tuple[DialogState, str]:
    # Extract slots before trusting the dialog act: misspelled preferences ("wast", "chep") are usually
    # classified as null, but the fuzzy matching can still recover them.
    new_preferences: Dict[rpe.StrEnum, str] = {}
    fuzzy_matched: Dict[rpe.StrEnum, str] = {}
    if state in (DialogState.INTRODUCTION, DialogState.ASK_PREFERENCES):
        fuzzy_slots = None
        if state == DialogState.ASK_PREFERENCES:
            missing_slot_type = next_missing_slot_type()
            fuzzy_slots = [missing_slot_type] if missing_slot_type else None
        new_preferences, fuzzy_matched = extract_preferences(utterance, fuzzy_slots=fuzzy_slots)

        # "Dont care" case was given, put a wildcard value
        if state == DialogState.ASK_PREFERENCES and missing_slot_type and not new_preferences and is_dont_care(utterance):
            new_preferences = {missing_slot_type: DONT_CARE}
            fuzzy_matched = {}

    # Repeatedly introduce and ask for user input until ther user provides us with more information.
    if state == DialogState.INTRODUCTION:
        if dialog_act == DialogAct.INFORM or new_preferences or fuzzy_matched:
            return handle_inform(new_preferences, fuzzy_matched)
        if dialog_act == DialogAct.HELLO:
            return DialogState.INTRODUCTION, INTO_SENTENCE
        if dialog_act == DialogAct.BYE:
            return DialogState.END, "Goodbye!"
        return DialogState.INTRODUCTION, get_repromt_for_missing_slots()

    if state == DialogState.ASK_PREFERENCES:
        if dialog_act == DialogAct.INFORM or new_preferences or fuzzy_matched:
            return handle_inform(new_preferences, fuzzy_matched)
        else:
            return DialogState.ASK_PREFERENCES, get_repromt_for_missing_slots()

    if state == DialogState.CONFIRM_SLOT:
        return handle_slot_confirmation(dialog_act, utterance)

    if state == DialogState.INFORM:
        if dialog_act == DialogAct.CONFIRM or dialog_act == DialogAct.AFFIRM:
            return DialogState.CONFIRM, "Great! I'll reserve that for you."
        if dialog_act == DialogAct.DENY or dialog_act == DialogAct.NEGATE:
            return DialogState.INFORM, offer_restaurant_suggestion(next_restaurant=True)
        if dialog_act == DialogAct.REQUEST:
            # TODO: get better keywords instead of just phone and address
            detail_type: RestaurantInfoType = None
            if "phone" in utterance.lower() or "number" in utterance.lower():
                detail_type = RestaurantInfoType.PHONE_NUMBER
            elif "address" in utterance.lower() or "location" in utterance.lower():
                detail_type = RestaurantInfoType.ADDRESS

            return DialogState.INFORM, get_restaurant_details(detail_type=detail_type)
        if dialog_act == DialogAct.RESTART:
            return DialogState.INTRODUCTION, intro_agg
    

    # This is basically hit anytime once the user has confirmed or thank you. TODO: probably bugs with this. needs testing    
    return DialogState.END, "We'll pick a restaurant for you! Coming soon in theaters :)"

def handle_inform(new_preferences: Dict[rpe.StrEnum, str], fuzzy_matched: Dict[rpe.StrEnum, str] = None) -> Tuple[DialogState, str]:
    """Stores every keyword-matched preference, overwriting any value that was already stored.
    Fuzzy-matched preferences are only stored after the user confirms them.
    Then asks for the next missing preference, or suggests a restaurant once all are known."""
    fuzzy_matched = fuzzy_matched or {}
    for info_request_type, info_request_value in new_preferences.items():
        slots[info_request_type].value = info_request_value

    if not new_preferences and not fuzzy_matched:
        return DialogState.ASK_PREFERENCES, get_repromt_for_missing_slots()

    # If there are any fuzzy-matched preferences, ask the user to confirm them before storing them
    pending_confirmations.update(fuzzy_matched)
    if pending_confirmations:
        return DialogState.CONFIRM_SLOT, confirmation_question()

    return ask_next_preference_or_suggest()

def handle_slot_confirmation(dialog_act: DialogAct, utterance: str) -> Tuple[DialogState, str]:
    slot_type, value = next(iter(pending_confirmations.items()))

    if dialog_act in (DialogAct.AFFIRM, DialogAct.CONFIRM, DialogAct.ACK):
        slots[slot_type].value = value
        del pending_confirmations[slot_type]
    elif dialog_act in (DialogAct.NEGATE, DialogAct.DENY):
        del pending_confirmations[slot_type]
        correction, _ = extract_preferences(utterance, fuzzy_slots=[])
        if slot_type in correction:
            slots[slot_type].value = correction[slot_type]
        elif not pending_confirmations:
            return DialogState.ASK_PREFERENCES, "Sorry about that. " + slots[slot_type].question
    else:
        return DialogState.CONFIRM_SLOT, "Sorry, I didn't catch that. " + confirmation_question()

    if pending_confirmations:
        return DialogState.CONFIRM_SLOT, confirmation_question()
    return ask_next_preference_or_suggest()

def confirmation_question() -> str:
    slot_type, value = next(iter(pending_confirmations.items()))
    if slot_type == rpe.Food:
        return f"Did you mean {value.title()} food?"
    if slot_type == rpe.Area:
        return f"Did you mean the {value} of town?"
    return f"Did you mean something {value}?"

def ask_next_preference_or_suggest() -> Tuple[DialogState, str]:
    # Ask for the first preference we don't know yet
    missing_slot = next_missing_slot()
    if missing_slot:
        return DialogState.ASK_PREFERENCES, missing_slot.question

    # All preferences are known, so suggest a restaurant and let the user confirm it.
    return DialogState.INFORM, offer_restaurant_suggestion()

def offer_restaurant_suggestion(next_restaurant: bool = False) -> str:
    global possible_restaurants, restaurant_index

    preferences = {}
    for info_request_type, slot in slots.items():
        if slot.value != DONT_CARE:
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
    rests = parser.fetch_resturant_by_info(rest_data, **pref_)
    return [r.title() for r in rests['restaurantname'].to_list()]

def get_restaurant_details(detail_type: RestaurantInfoType = None) -> str:
    #details = possible_restaurants[restaurant_index].details TODO: wait for Jesse to implement this
    if detail_type == RestaurantInfoType.PHONE_NUMBER:
        return "Phone number is 123-456-7890."
    elif detail_type == RestaurantInfoType.ADDRESS:
        return "Address is 123 Main St."
    else:
        return "Phone number is 123-456-7890. Address is 123 Main St."

def next_missing_slot() -> Slot:
    slot_type = next_missing_slot_type()
    return slots[slot_type] if slot_type else None

def next_missing_slot_type() -> rpe.StrEnum:
    for slot_type, slot in slots.items():
        if not slot.filled:
            return slot_type
    return None

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

def extract_preferences(utterance: str, fuzzy_slots: List[rpe.StrEnum] = None) -> Tuple[Dict[rpe.StrEnum, str], Dict[rpe.StrEnum, str]]:
    """Keyword matches every slot, then falls back to fuzzy matching for the slots that are still missing.
    Returns (keyword matches, fuzzy matches) so fuzzy matches can be confirmed with the user."""
    preferences: Dict[rpe.StrEnum, str] = extract_slots_keyword(utterance)
    fuzzy_preferences: Dict[rpe.StrEnum, str] = {}
    candidate_slots = fuzzy_slots if fuzzy_slots is not None else list(slots)
    missing_slots = [slot_type for slot_type in candidate_slots if slot_type not in preferences]

    if not missing_slots or match_type is None:
        return preferences, fuzzy_preferences

    if match_type == MatchType.LEVENSHTEIN:
        words = utterance.lower().split()
        for slot_type in missing_slots:
            for word in words:
                # Short words like "the" or "eat" are too close to real keywords to fuzzy match safely.
                if len(word) < LEVENSHTEIN_MIN_WORD_LENGTH:
                    continue
                match = get_word_with_levenshtein_distance(word, list(slot_type), LEVENSHTEIN_MAX_DISTANCE)
                if match is not None:
                    fuzzy_preferences[slot_type] = match
                    break
    elif match_type == MatchType.SEMANTIC_EMBEDDINGS:
        semantic_slots = extract_slots_semantic(utterance)
        for slot_type in missing_slots:
            if slot_type in semantic_slots:
                fuzzy_preferences[slot_type] = semantic_slots[slot_type]

    return preferences, fuzzy_preferences


def classify(model: Models, input_path: str, utterance: str) -> DialogAct:
    return DialogAct(run_str(model=model, input_path=input_path, phrases=[utterance])[0])


def output_to_user(system_utterance, do_tts):
    # For the GPT sim, it takes too long with TTS if they are not parallel. 
    threading.Thread(
        target=print,
        args=(f'System: {system_utterance}',),
        daemon=True,
    ).start()

    if do_tts:
        tts.gen_and_play_tts(system_utterance)


if __name__ == '__main__':
    kwargs = dialog_arg_parser()
    if kwargs['tts']:
        tts.load_pipeline()
    if kwargs['simllm']:
        print = parser.enable_gpt_like_typing()

    model_name = kwargs['model']
    input_path = f'model_files/{model_name}.joblib'
    match_type = kwargs['match_type']

    model = MODEL_NAMES_DIALOG[model_name]

    output_to_user(INTO_SENTENCE, kwargs['tts'])
    output_to_user(INTRO_PROMPT, do_tts=False)

    state = DialogState.INTRODUCTION

    while True:
        user_input = input("You: ")

        if user_input == 'QUIT':
            break

        dialog_act: DialogAct = classify(model, input_path, user_input)
        state, system_utterance = state_transition(state, dialog_act, user_input)
        
        output_to_user(system_utterance, kwargs['tts'])

        if state == DialogState.END:
            break
