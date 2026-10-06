import re
import csv
from src.models.rule_based_baseline import contains_keyword

DATA_PATH = "data/restaurant_info.csv"

#used to collect all the different food types from restaurant_info.csv
def get_food_types():
    food_types = set()

    with open(DATA_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            food_types.add(row["food"])

    return sorted(food_types)


FOOD_TYPES = get_food_types()

PRICE_TYPES = (
    "cheap",
    "moderate",
    "expensive",
)

AREAS = (
    "north", 
    "east",
    "south",
    "west",
    "centre",
)

def extract_slots_keyword(utterance):
    text = utterance.lower()

    slots = {}

    #food slot
    for food in FOOD_TYPES:
        if contains_keyword(text, food):
            slots["food"] = food
            break

    #price slot
    for price in PRICE_TYPES: 
        if contains_keyword(text, price):
            slots["pricerange"] = price
            break

    #area slot
    for area in AREAS:
        if contains_keyword(text, area):
            slots["area"] = area
            break

    return slots

if __name__ == "__main__":
    print(
        extract_slots_keyword(
            "I am looking for an expensive Italian restaurant in the north" #testing if it works 
        )
    )
