import re
import csv
import Levenshtein

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


# 1. Keyword matching
def extract_slots_keyword(utterance):
    text = utterance.lower()

    slots = {}

    #Food slot
    for food in Food:
        if contains_keyword(text, food.value):
            slots["food"] = food.value
            break

    #Price slot
    for price in PriceRange:
        if contains_keyword(text, price.value):
            slots["pricerange"] = price.value
            break

    #Area slot
    for area in Area:
        if contains_keyword(text, area.value):
            slots["area"] = area.value
            break

    return slots


# 2. Levenshtein distance
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


# 3. Semantic similarity via DistilBERT embeddings
def find_semantic_match(text, possible_values, threshold=0.7):
    possible_values = list(possible_values)

    value_texts = [value.value for value in possible_values]

    texts = [text] + value_texts

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
        return best_value.value

    return None


def extract_slots_semantic(utterance, threshold=0.7):
    text = utterance.lower()
    words = re.findall(r"\b\w+\b", text)

    slots = {}

    #Food
    for word in words:
        match = find_semantic_match(
            word,
            Food,
            threshold
        )

        if match is not None:
            slots["food"] = match
            break

    #Price
    for word in words:
        match = find_semantic_match(
            word,
            PriceRange,
            threshold
        )

        if match is not None:
            slots["pricerange"] = match
            break

    #Area
    for word in words:
        match = find_semantic_match(
            word,
            Area,
            threshold
        )

        if match is not None:
            slots["area"] = match
            break

    return slots


if __name__ == "__main__":
    print(
        extract_slots_keyword(
            "I am looking for an expensive Italian restaurant in the north"
        )
    )

    print(levenshtein_distance("exxpensive"))

    print(
        extract_slots_semantic(
            "I am looking for a fancy Italian restaurant in the north"
        )
    )