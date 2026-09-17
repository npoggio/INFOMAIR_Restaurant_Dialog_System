"""A module to write parsers in that will be used to read .dat files"""
from typing import List, Tuple, Optional

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
        # Check for str type
        if not isinstance(phrase, str):
            raise ValueError(f"Line #{idx} in `dat_lines` is type `{type(phrase)}` where it should be `str`")

        if remove_apostraphes:
            phrase = phrase.replace("'", '')

        if do_lower:
            # Better form of lowering for making text uniform.
            phrase = phrase.casefold()  

        # Split the phrase, and remove if no space
        split_phrase: List[str] = phrase.split(' ')
        if len(split_phrase) < 2:
            if verbose:
                print(f'Line #{idx} is not in the correct format ("CLASS [SPACE] UTTERANCE"): {phrase}')
            continue  # Skip a cycle

        # (First), (Second -> Last)
        classified_phrase: List[Tuple[str, str]] = split_phrase[0], split_phrase[1:]
        pairs.append(classified_phrase)
        
    return pairs        


# For testing, wil only run when this module is called upon specifically
if __name__ == '__main__':
    file_path: str = 'data/dialog_acts.dat'
    n_lines: int = 5

    dat_lines: List[str] = read_text_file_lines(file_path=file_path)
    print(*dat_lines[:n_lines], sep='\n')

    do_lower: bool = True
    remove_apostrophes: bool = True
    verbose: bool = True
    parsed_dat_file = parse_dstc_dat_file(dat_lines=dat_lines, do_lower=do_lower)
    print(*parsed_dat_file[:n_lines], sep='\n')
