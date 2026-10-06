import Levenshtein
import pandas as pd
from src.enums.restaurant_props import PriceRange, Area, Food

restaurants = pd.read_csv("restaurant_info.csv")
# if keyword_match fails check distances to 
def levenshtein_distance(sentence):
    words = sentence.split()
    possible_values = list(PriceRange) + list(Area) + list(Food)
    closest_match = None
    lowest_distance = float("inf")
    for value in possible_values:
        for word in words:
            word = word.lower()
            # Do not suggest a correction for an already correct value.
            if word == value.value:
                continue

            distance = Levenshtein.distance(
                word.lower(),
                value.value.lower()
            )

            if distance < lowest_distance:
                lowest_distance = distance
                closest_match = value

    if closest_match is None:
        return None

    return f"Did you maybe mean {closest_match.value}?"

print(levenshtein_distance("do you have cheap sponish food"))


from src.utils.distilbert_embeddings import get_distilbert_embeddings
from sklearn.metrics.pairwise import cosine_similarity


def semantic_similarity(sentence):
    embedded_keywords = get_distilbert_embeddings(None, [sentence])
    possible_values = list(PriceRange) + list(Area) + list(Food)
    closest_match = None
    highest_similarity = float("-inf")

    for i in possible_values:
        embedded_value = get_distilbert_embeddings(None, [i.value])
        similarity = cosine_similarity(
            embedded_keywords,
            embedded_value
        )[0][0]

        if similarity > highest_similarity:
            highest_similarity = similarity
            closest_match = i
    
    return f"Did you maybe mean {closest_match.value.lower()}"

print(semantic_similarity("i would like food from spain"))

    





