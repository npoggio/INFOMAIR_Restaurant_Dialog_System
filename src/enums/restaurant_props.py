from enum import StrEnum


class PriceRange(StrEnum):
    CHEAP = 'cheap'
    MODERATE = 'moderate'
    EXPENSIVE = 'expensive'


class Area(StrEnum):
    CENTRE = 'centre'
    NORTH = 'north'
    EAST = 'east'
    SOUTH = 'south'
    WEST = 'west'


class Food(StrEnum):
    BRITISH = 'british'
    MODERN_EUROPEAN = 'modern european'
    ITALIAN = 'italian'
    ROMANIAN = 'romanian'
    SEAFOOD = 'seafood'
    CHINESE = 'chinese'
    STEAKHOUSE = 'steakhouse'
    ASIAN_ORIENTAL = 'asian oriental'
    FRENCH = 'french'
    PORTUGUESE = 'portuguese'
    INDIAN = 'indian'
    SPANISH = 'spanish'
    EUROPEAN = 'european'
    VIETNAMESE = 'vietnamese'
    KOREAN = 'korean'
    THAI = 'thai'
    MOROCCAN = 'moroccan'
    SWISS = 'swiss'
    FUSION = 'fusion'
    GASTROPUB = 'gastropub'
    TUSCAN = 'tuscan'
    INTERNATIONAL = 'international'
    TRADITIONAL = 'traditional'
    MEDITERRANEAN = 'mediterranean'
    POLYNESIAN = 'polynesian'
    AFRICAN = 'african'
    TURKISH = 'turkish'
    BISTRO = 'bistro'
    NORTH_AMERICAN = 'north american'
    AUSTRALASIAN = 'australasian'
    PERSIAN = 'persian'
    JAMAICAN = 'jamaican'
    LEBANESE = 'lebanese'
    CUBAN = 'cuban'
    JAPANESE = 'japanese'
    CATALAN = 'catalan'


class FoodQuality(StrEnum):
    GOOD = 'good'
    MEDIOCRE = 'mediocre'


class Crowdedness(StrEnum):
    NOT_BUSY = 'not busy'
    BUSY = 'busy'


class LengthOfStay(StrEnum):
    LONG = 'long'
    SHORT = 'short'
