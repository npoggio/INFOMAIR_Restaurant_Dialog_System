import Levenshtein
import pandas as pd
from src.enums.restaurant_props import PriceRange, Area, Food

restaurants = pd.read_csv("restaurant_info.csv")
# if keyword_match fails check distances to 
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

    return f"Did you maybe mean {closest_match.value}?"

print(levenshtein_distance("exxpnsive"))




