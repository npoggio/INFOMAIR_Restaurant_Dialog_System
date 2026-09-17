""""""
from typing import List, Tuple
import nltk
import parser
from sklearn.feature_extraction.text import CountVectorizer

UNK_TOKEN = '<UNK>'


def tokenize(dialog_acts: List[Tuple[str, str]]):


    # Transpose dialog acts so we get <classes, phrases> (y, X; but in text still)
    classes, phrases = list(zip(*dialog_acts))

    cv = CountVectorizer()
    cv.fit_transform(raw_documents=phrases, y=classes)


if __name__ == '__main__':
    n_rows = 5

    file_path = 'data/dialog_acts.dat'
    dat_lines = parser.read_text_file_lines(file_path)
    dialog_acts = parser.parse_dstc_dat_file(dat_lines)
    #print(*dialog_acts[:n_rows], sep='\n')

    I = 0
    tokenize(dialog_acts[:n_rows])
