"""A module to write parsers in that will be used to read .dat files"""
from typing import List, Tuple, Optional, Iterable
from src.enums.restaurant_props import (
    PriceRange, Area, Food, FoodQuality, 
    Crowdedness, LengthOfStay )
import enum
import numpy as np
import pandas as pd
import inspect

TEXTUAL_FILE_TYPES = '.txt', '.dat'


def read_text_file_lines(file_path: str) -> List[str]:
    """
    Reads the lines of a textual based file

    :param str file_path: The path to a file that is to be read
    :returns: A list of lines from the passed document
    :rtype: List[str]
    """

    # Throw error if not a textual file
    if not isinstance(file_path, str):
        raise TypeError(
            '`file_path` parameter needs to be a path to a text file (`str`) but is a `{}`'.format(
                type(file_path)
            ))
    
    if not file_path.lower().endswith(TEXTUAL_FILE_TYPES):
        raise ValueError(
            '`file_path` must be a text-based file, only {} files are allowed'.format(
                ','.join(TEXTUAL_FILE_TYPES)
            ))

    with open(file_path, encoding='utf-8') as file:
        text: str = file.read()
        # Using split instead of readlines to remove the '\n' in the process
        lines: List[str] = text.split('\n')

    return lines
    

def sanitize_phrase(phrase: str, 
                    do_lower: bool = True, 
                    remove_apostraphes: bool = True) -> str:

    # Check for str type
    if not isinstance(phrase, str):
        raise ValueError(f"Line #{idx} in `dat_lines` is type `{type(phrase)}` where it should be `str`")

    if remove_apostraphes:
        phrase = phrase.replace("'", '')

    if do_lower:
        # Better form of lowering for making text uniform.
        phrase = phrase.casefold()  

    # Split the phrase, and remove if no space
    return phrase


def parse_dstc_dat_file(dat_lines: List[str], 
                        do_lower: bool = True, 
                        remove_apostraphes: bool = True,
                        verbose: bool = True) -> List[Tuple[str, str]]:
    """
    Parses the lines of the DSTC2-based data file where the format is:
    "CLASS [SPACE] UTTERANCE". When a faulty line is discovered 

    :param str dat_lines: Lines from the .dat file. Possibly read with `read_text_file_lines`
    :param bool do_lower: Whether to lower the text (Optional, default=True)
    :param bool remove_apostrophes: Whether to remove apostrophes from the text (Optinal, default=True)
    :param bool verbose: Whether to print parsing errors (Optional, default=True)
    :returns: A list of all the classes and utterences in a tuple: (CLASS, UTTERANCE)
    :rtype: List[Tuple[str, str]]
    """

    pairs: List[Tuple[str, str]] = []

    for idx, phrase in enumerate(dat_lines):
        # Some files have a trailing empty line, we don't want to give a warning for that
        if (idx == len(dat_lines) - 1) and (phrase == ''):
            continue

        sanitized_phrase = sanitize_phrase(phrase=phrase, 
                                           do_lower=do_lower, 
                                           remove_apostraphes=remove_apostraphes)
        split_phrase = sanitized_phrase.split(' ', maxsplit=1)
        
        if len(split_phrase) < 2:
            # Verbose, but not trailing whitespace
            if verbose and not ((idx == len(dat_lines) - 1) and (phrase == '')):
                print(f'Line #{idx} is not in the correct format ("CLASS [SPACE] UTTERANCE"): {phrase}')
            continue  # Skip a cycle

        # (First), (Second -> Last)
        classified_phrase: Tuple[str, str] = split_phrase[0], split_phrase[1]
        pairs.append(classified_phrase)
        
    return pairs        


def load_restaurant_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def fetch_resturant_by_info(
        _restaurant_info: pd.DataFrame,
        restaurantname: Optional[str] = None,
        pricerange: Optional[PriceRange|Iterable[PriceRange]] = None,
        area: Optional[Area|Iterable[Area]] = None,
        food: Optional[Food|Iterable[Food]] = None,
        phone: Optional[str] = None,
        addr: Optional[str] = None,
        postcode: Optional[str] = None,
        food_quality: Optional[FoodQuality|Iterable[FoodQuality]] = None,
        crowdedness: Optional[Crowdedness|Iterable[Crowdedness]] = None,
        length_of_stay: Optional[LengthOfStay|Iterable[LengthOfStay]] = None,):
    """
    Fetch the restaurants with the corresponding values, 
    a list can be passed into the slots to indicate multiple options (OR)
    """
    arguments = locals()

    for colname, filtervalue in arguments.items():
        # Skip not-wanted values
        if colname.startswith('_'): continue
        if filtervalue is None: continue

        # When a list is passed you can pass multiple values
        if isinstance(filtervalue, Iterable) and not isinstance(filtervalue, (enum.Enum, str)):
            mask = _restaurant_info[colname].isin(filtervalue)
        else:
            mask = _restaurant_info[colname] == filtervalue

        _restaurant_info = _restaurant_info[mask]

    return _restaurant_info


# For testing, wil only run when this module is called upon specifically
if __name__ == '__main__':
    file_path: str = 'data/restaurant_info_extended.csv'
    rest_data = load_restaurant_data(file_path)
    restaurants = fetch_resturant_by_info(
        rest_data,
        restaurantname = None,
        pricerange = None,
        area = Area.CENTRE,
        food = [Food.ASIAN_ORIENTAL, Food.ITALIAN],
        postcode = None,
        food_quality = None,
        crowdedness = Crowdedness.BUSY,
        length_of_stay = None,
    )

    print(restaurants)

    #for col in rd:
    #    print("========", col)
    #    uq = rd[col].unique()
    #    print(*[f"{str(u).upper().replace(' ', '_')} = {repr(str(u))}" for u in uq], sep='\n')


    #file_path: str = 'data/dialog_acts.dat'
    #n_lines: int = 5

    #dat_lines: List[str] = read_text_file_lines(file_path=file_path)
    #print(*dat_lines[:n_lines], sep='\n')

    #verbose: bool = True
    #parsed_dat_file = parse_dstc_dat_file(dat_lines=dat_lines)
    #print(*parsed_dat_file[:n_lines], sep='\n')
