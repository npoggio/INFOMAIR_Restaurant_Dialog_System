from enum import StrEnum

# The names of these enums matter and should not be changed as the restaurant
# fetching logic depends on them for column names :)


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


class Food_Quality(StrEnum):
    GOOD = 'good'
    MEDIOCRE = 'mediocre'


class Crowdedness(StrEnum):
    NOT_BUSY = 'not busy'
    BUSY = 'busy'


class Length_Of_Stay(StrEnum):
    LONG = 'long'
    SHORT = 'short'

class RestaurantInfoType(StrEnum):
    PHONE_NUMBER = 'phone number'
    ADDRESS = 'address'