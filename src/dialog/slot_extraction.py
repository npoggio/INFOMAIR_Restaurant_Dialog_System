import re
import csv
import Levenshtein

from src.enums.restaurant_props import PriceRange, Area, Food
from src.enums.dont_care import DontCare
from src.models.rule_based_baseline import contains_keyword
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.distilbert_embeddings import get_distilbert_embeddings

DATA_PATH = "data/restaurant_info_extended.csv"


# Used to collect all the different food types from restaurant_info.csv
def get_food_types():
    food_types = set()

    with open(DATA_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            food_types.add(row["food"])

    return sorted(food_types)


FOOD_TYPES = get_food_types()


def is_dont_care(utterance):
    text = utterance.lower()
    return any(re.search(rf"\b{re.escape(phrase.value)}", text) for phrase in DontCare)


# 1. Keyword matching
def extract_slots_keyword(utterance):
    text = utterance.lower()

    slots = {}

    # Food slot
    for food in Food:
        if contains_keyword(text, food.value):
            slots[Food] = food.value
            break

    # Price slot
    for price in PriceRange:
        if contains_keyword(text, price.value):
            slots[PriceRange] = price.value
            break

    # Area slot
    for area in Area:
        if contains_keyword(text, area.value):
            slots[Area] = area.value
            break

    return slots


# 2. Levenshtein distance
def get_word_with_levenshtein_distance(mismatched_keyword, possible_values=None, max_distance=None):
    if possible_values is None:
        possible_values = list(PriceRange) + list(Area) + list(Food)

    closest_match = None
    lowest_distance = float("inf")
    is_tie = False

    for value in possible_values:
        distance = Levenshtein.distance(
            mismatched_keyword.lower(),
            value.value.lower()
        )

        if distance < lowest_distance:
            lowest_distance = distance
            closest_match = value
            is_tie = False
        elif distance == lowest_distance:
            is_tie = True

    if max_distance is not None and lowest_distance > max_distance:
        return None

    if is_tie:
        return None

    return closest_match.value


# 3. Semantic similarity via DistilBERT embeddings
def find_semantic_match(text, possible_values, threshold=0.7):
    possible_values = list(possible_values)

    # Convert enum values to strings
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

    #print('\n', text)
    #print(*list(zip(possible_values, similarities)), sep='\n')

    best_index = similarities.argmax()
    best_similarity = similarities[best_index]
    best_value = possible_values[best_index]

    if best_similarity >= threshold:
        return best_value.value, best_similarity

    return None, 0


EXTRACTABLE_SLOTS = [Food, PriceRange, Area]


def phrase_to_ngram(phrase, max_ngram=3):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", phrase.lower())
    tokens = re.findall(r"\b\w+\b", cleaned)

    if not tokens:
        return [phrase.lower()]

    if len(tokens) < max_ngram:
        return [" ".join(tokens)] if tokens else [phrase.lower()]

    ngrams = []
    for i in range(len(tokens) - 2):
        ngrams.append(" ".join(tokens[i:i + max_ngram]))

    return list(dict.fromkeys(ngrams))


def extract_slots_semantic(utterance, threshold=0.90):
    text = utterance.lower()
    words = phrase_to_ngram(text, 1)

    slots = {}

    for slot in EXTRACTABLE_SLOTS:
        match, best_match, best_score = None, None, 0 
        for word in words:
            match, score = find_semantic_match(
                word,
                slot,
                threshold
            )

            if score > best_score:
                best_match, best_score = match, score

        if match is not None:
            slots[slot] = best_match
            
    return slots


if __name__ == "__main__":
    #print(
    #    extract_slots_keyword(
    #        "I am looking for an expensive Italian restaurant in the north"
    #    )
    #)
    #
    #print(get_word_with_levenshtein_distance("exxpensive"))
    #
    #print(
    #    extract_slots_semantic(
    #        "I am looking for a fancy Italian restaurant in the north"
    #    )
    #)
    print(extract_slots_semantic("I am looking for a high-end continental restaurant in the uptown"))