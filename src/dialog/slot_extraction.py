import re
import csv
import Levenshtein
import pandas as pd

from src.enums.restaurant_props import PriceRange, Area, Food
from src.models.rule_based_baseline import contains_keyword
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.distilbert_embeddings import get_distilbert_embeddings


DATA_PATH = "data/restaurant_info.csv"

# Used to collect all the different food types from restaurant_info.csv
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

# 1. Keyword matching 
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

# 2. Levenshtein distances
restaurants = pd.read_csv("restaurant_info.csv")

#if keyword_match fails check distances to 
def levenshtein_distance(mismatched_keyword):
    possible_values = list(PriceRange) + list(Area) + list(Food)
    closest_match = None
    lowest_distance = float("inf")
    for value in possible_values:
        distance = Levenshtein.distance(
            mismatched_keyword.lower(),
            value.value.lower()
        )

        if distance < lowest_distance:
            lowest_distance = distance
            closest_match = value

    return f"Did you mean {closest_match.value}?"

print(levenshtein_distance("exxpnsive"))

# 3. Semantic similarity via embeddings
def find_semantic_match(text, possible_values, threshold=0.7):
    possible_values = list(possible_values)

    texts = [text] + possible_values

    embeddings = get_distilbert_embeddings(
        None,
        texts=texts
    )

    text_embedding = embeddings[0:1]
    value_embeddings = embeddings[1:]

    similarities = cosine_similarity(
        text_embedding,
        value_embeddings
    )[0]

    best_index = similarities.argmax()
    best_similarity = similarities[best_index]
    best_value = possible_values[best_index]

    if best_similarity >= threshold:
        return best_value

    return None

def extract_slots_semantic(utterance, threshold=0.7):
    text = utterance.lower()
    slots = {}

    #food
    for word in words:
        match = find_semantic_match(
            word, 
            FOOD_TYPES,
            threshold
        )

        if match is not None:
            slots["food"] = match
            break

    #price
    for word in words:
            match = find_semantic_match(
                word, 
                PRICE_TYPES,
                threshold
            )
    
            if match is not None:
                slots["pricerange"] = match
                break

    #area
    for word in words:
            match = find_semantic_match(
                word, 
                AREAS,
                threshold
            )
    
            if match is not None:
                slots["area"] = match
                break

    return slots
    

if __name__ == "__main__":
    print(
        extract_slots_keyword(
            "I am looking for an expensive Italian restaurant in the north" #testing if it works 
        )
    )
