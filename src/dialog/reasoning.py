from typing import Dict, List
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


TEXTS_INDIPENDANT = {
    Touristic: "a touristy restaurant",
    Children: "a child friendly restaurant",
    Assigned_Seats: "a restaurant with assigned seats",
    Romantic: "a romantic place",
}
TEXTS_COMBINED = {
    Touristic: "a touristy",
    Children: "a child friendly",
    Assigned_Seats: "an assigned-seat",
    Romantic: "a romantic",
}


__GENERIC_QUERY = ""
__AGG_PREFS_TEXT = "{confl_prefl} or a {confl_prefr} {confl_class}"
__CONFLICTING_Q0 = "You mentioned you'd like a {confl_prefl} {confl_class} restaurant. However, this conflicts with your " \
"{confl_class} preference of {confl_prefr}. Would you like a {agg_prefs} restaurant"
__CONFLICTING_Q1 = "You mentioned you'd like {logic_pref}. However, this conflicts with your " \
"{confl_class} preference of {confl_prefr}. Would you like a {agg_prefs} restaurant"
__CONFLICTING_P_REASON = "You mentioned you'd like {logic_prefs} restaurant. However, these preferences clash in a couple of areas: "


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



def find_conflicting(pref_default: Dict[StrEnum, str], pref_logic: Dict[StrEnum, str]):
    overlapping_keys = pref_default.keys() & pref_logic.keys()
    conflicting_keys = {
        key: (pref_default[key], pref_logic[key]) for key in overlapping_keys
        if pref_default[key] is not pref_logic[key]
    }

    return conflicting_keys


def check_for_conflicting_reasonings(reasonings: List[Dict[StrEnum, str]]):
    reasoning_conflicts = {}

    # Compare all 
    for (reas_a), (reas_b) in combinations(reasonings, 2):
        conflicts = find_conflicting(reas_a, reas_b)
        if len(conflicts) == 0:
            continue

        reasoning_conflicts.update(conflicts)

    return reasoning_conflicts


def reasoning_dialog_manager():


TOURISTIC = {
    PriceRange: PriceRange.CHEAP,
    Food_Quality: Food_Quality.GOOD,
    Not_Food: Not_Food.ROMANIAN
}

CHILDREN = {
    Length_Of_Stay: Length_Of_Stay.SHORT
}

ASSIGNED_SEATS = {
    Crowdedness: Crowdedness.BUSY
}

ROMANTIC = {
    Crowdedness: Crowdedness.NOT_BUSY,
    Length_Of_Stay: Length_Of_Stay.LONG
}


if __name__ == '__main__':
    confl = find_conflicting(ROMANTIC, ASSIGNED_SEATS)


    check_for_conflicting_reasonings((ROMANTIC, ASSIGNED_SEATS, CHILDREN))

    #for conflicting_class, conflicting_values in confl.items():
    #    cq = ask_to_resolve_conflicting(conflicting_class,
    #                               conflicting_values,
    #                               romantic=True,
    #                               assigned_seats=True)
    #    print(cq)
    #print(confl)