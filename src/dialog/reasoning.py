from typing import Dict, List, Iterable, Optional, Tuple
from enum import StrEnum
from itertools import combinations
from src.enums.restaurant_props import (
    Area, PriceRange, Food, Romantic, Not_Food,
    Touristic, Assigned_Seats, Children,
    Crowdedness, Food_Quality, Length_Of_Stay
    )


#def create_touristic(pricerange, food_quality, food):
#    if (pricerange       == PriceRange.CHEAP 
#        and food_quality == Food_Quality.GOOD 
#        and food         != Food.ROMANIAN):
#        return Touristic.YES
#    else:
#        return Touristic.NO
#
#
#def create_romantic(crowdedness, length_of_stay):
#    if (crowdedness == Crowdedness.NOT_BUSY and length_of_stay == Length_Of_Stay.LONG):
#        return Romantic.YES
#    else:
#        return Romantic.NO
#
#
#def create_children(length_of_stay):
#    if length_of_stay == Length_Of_Stay.SHORT:
#        return Children.YES
#    else:
#        return Children.NO
#
#
#def create_assigned_seats(crowdedness):
#    if crowdedness == Crowdedness.BUSY:
#        return Assigned_Seats.YES
#    else:
#        return Assigned_Seats.NO

REASONING_SLOTS = (Touristic, Children, Assigned_Seats, Romantic)

LOGIC_TEXTS = {
    Touristic: "a touristy",
    Children: "a child friendly",
    Assigned_Seats: "an assigned-seat",
    Romantic: "a romantic",
}

REASONING_EXPLOSION = {
    Touristic: {
        PriceRange: PriceRange.CHEAP,
        Food_Quality: Food_Quality.GOOD,
        Not_Food: Not_Food.ROMANIAN
    },
    Children: {
        Length_Of_Stay: Length_Of_Stay.SHORT
    },
    Assigned_Seats: {
        Crowdedness: Crowdedness.BUSY
    },
    Romantic: {
        Crowdedness: Crowdedness.NOT_BUSY,
        Length_Of_Stay: Length_Of_Stay.LONG
    }
}

__AGG_PREFS_TEXT = "{confl_prefl} or a {confl_prefr} {confl_class}"
__CONFLICTING_Q0 = "You mentioned you'd like a {confl_prefl} {confl_class} restaurant. However, this conflicts with your " \
"another indicated preference of {confl_prefr}. Would you like a {confl_prefl} or {confl_prefr} restaurant?"
_CONFLICTING_QR = "You mentioned you'd like {logic_prefl} and {logic_prefr} restaurant. However, this clashes in the form of {confl_class}. Would you like {prefl} or {prefr}"

reasoning_slots_filter = lambda enum, slot: (issubclass(enum, REASONING_SLOTS)) and (str(slot.value) == 'yes')

def ask_to_resolve_conflicting(conflicting_class, 
                               conflicticn_values,
                               touristic: bool = False, 
                               children: bool = False, 
                               assigned_seats: bool = False, 
                               romantic: bool = False):
    logic_pref: str 
    logic_clash = True

    if touristic:
        logic_pref = __TOURISTIC_TEXT
    elif children:
        logic_pref = __CHILDREN_TEXT
    elif assigned_seats:
        logic_pref = __ASSIGNED_SEATS_TEXT
    elif romantic:
        logic_pref = __ROMANTIC_TEXT
    else:
        logic_clash = False

    confl_class_text = conflicting_class.__name__.lower().replace('_', ' ')
    confl_prefl=conflicticn_values[0].value
    confl_prefr=conflicticn_values[1].value
    agg_prefs = __AGG_PREFS_TEXT.format(confl_class=confl_class_text, 
                                        confl_prefl=confl_prefl, 
                                        confl_prefr=confl_prefr)

    if not logic_clash:
        out = __CONFLICTING_Q0.format(
            confl_prefr = confl_prefr,
            confl_class = confl_class_text,
            agg_prefs = agg_prefs
        )
    else:
        out = __CONFLICTING_Q1.format(
            logic_pref = logic_pref,
            confl_prefr = confl_prefr,
            confl_class = confl_class_text,
            agg_prefs = agg_prefs
        )

    return out


def ask_to_resolve_conflicting_reasonings(conflicting_reasonings: Dict[StrEnum, Tuple[Tuple[StrEnum, StrEnum], Tuple[str, str]]]):
    handled_enums = set()
    
    for confl_class, ((logic_prefl, logic_prefr), (prefl, prefr)) in conflicting_reasonings.items():
        if confl_class in handled_enums:
            continue

        question = _CONFLICTING_QR.format(
            logic_prefl=LOGIC_TEXTS[logic_prefl], 
            logic_prefr=LOGIC_TEXTS[logic_prefr], 
            confl_class=confl_class.__name__.lower().replace('_', ' '), 
            prefl=prefl, 
            prefr=prefr
        )

        handled_enums.add(confl_class)  # type: ignore
        yield (confl_class, question)
    return handled_enums


def ask_to_resolve_generic_reasonings(conflicts):
    for enum_class, (confl_prefl, confl_prefr) in conflicts.items():
        question = __CONFLICTING_Q0.format(
            confl_class = enum_class.__name__.lower().replace('_', ' '),
            confl_prefl = confl_prefl.value,
            confl_prefr = confl_prefr.value
        )
        yield enum_class, question


def find_conflicting(pref_default: Dict[StrEnum, str], pref_logic: Dict[StrEnum, str]):
    overlapping_keys = pref_default.keys() & pref_logic.keys()
    conflicting_keys = {
        key: (pref_default[key], pref_logic[key]) for key in overlapping_keys
        if pref_default[key] is not pref_logic[key]
    }

    return conflicting_keys


def check_for_conflicting_reasonings(reasonings: List[Dict[StrEnum, str]], 
                                     reasoning_classes: List[StrEnum]) -> Dict[StrEnum, Tuple[Tuple[StrEnum, StrEnum], Tuple[str, str]]]:
    """
    Returns a dictionary of all the conflicting Slot Categories as keys and a pair of values with the first being a tuple
    of two reasoning options (i.e. Romantic, Assigned_Seats) and a second pair of the options.
    """
    reasoning_conflicts = {}
    embedded_reasonings = zip(reasoning_classes, reasonings)

    # Compare all 
    for (reas_class_a, reas_a), (reas_class_b, reas_b) in combinations(embedded_reasonings, 2):
        conflicts = find_conflicting(reas_a, reas_b)
        if len(conflicts) == 0:
            continue

        updated_conflicts = {conflict_enum: ((reas_class_a, reas_class_b), conflict_values) 
                             for conflict_enum, conflict_values in conflicts.items()}
        reasoning_conflicts.update(updated_conflicts)

    return reasoning_conflicts


def generic_dialog_handler(preferences_a, preferences_b):
    non_reasoning_slots_a = {enum: slot for enum, slot in preferences_a.items() if not reasoning_slots_filter(enum, slot)}
    non_reasoning_slots_b = {enum: slot for enum, slot in preferences_b.items() if not reasoning_slots_filter(enum, slot)}
    conflicts = find_conflicting(non_reasoning_slots_a, non_reasoning_slots_b)

    return ask_to_resolve_generic_reasonings(conflicts)


def reasoning_dialog_handler(slots: Dict[StrEnum, 'Slot'], reasoning_slots_out):
    # Get all reasoning slots, explode them and check for conflicts
    reasoning_slots = {enum: slot for enum, slot in slots.items() if reasoning_slots_filter(enum, slot)}
    exploded_reasoning_slots = [REASONING_EXPLOSION[slot] for slot in reasoning_slots]
    [reasoning_slots_out.update(reasoning_slot_exploded) for reasoning_slot_exploded in exploded_reasoning_slots]
    exploded_reasoning_classes = list(reasoning_slots.keys())

    conflicting_reasonings = check_for_conflicting_reasonings(exploded_reasoning_slots, exploded_reasoning_classes)
    return ask_to_resolve_conflicting_reasonings(conflicting_reasonings)


# @TODO: ADD SLOT EXTRACTION!
def reasoning(slots) -> Dict[StrEnum, str]:
    slots = slots.copy()
    new_slots = {}
    reason_question_generator = reasoning_dialog_handler(slots, reasoning_slots_out=new_slots)
    slots_handled = set()

    # The reason_question_generator is a generator
    for (slot, question) in reason_question_generator:
        slots_handled.add(slot)
        user_input = input('System: ' + question + "\nYou: ")
        # @TODO: Do some slot extraction stuff bla bla bla
        new_slots[slot] = user_input

    for handled in slots_handled:
        if handled in slots:
            del slots[handled]
    
    generic_question_generator = generic_dialog_handler(new_slots, slots)
    slots = slots | new_slots

    for (slot, question) in generic_question_generator:
        user_input = input('System: ' + question + "\nYou: ")
        # @TODO: Do some slot extraction stuff bla bla bla
        slots[slot] = user_input

    return slots
    

if __name__ == '__main__':
    from src.dialog_manager import Slot

    slots = {
        Crowdedness: Slot('', value=Crowdedness.BUSY),
        Length_Of_Stay: Slot('', value=Length_Of_Stay.SHORT),     
        Romantic: Slot('', value=Romantic.YES),
        Assigned_Seats: Slot('', value=Assigned_Seats.YES),
    }

    r = reasoning(slots)
    print(r)