""""""
import os
from typing import List, Tuple, Dict, Iterable, Callable, Any
import joblib
from . import parser
import numpy as np
from scipy.sparse import spmatrix
from sklearn.feature_extraction.text import CountVectorizer

UNK_TOKEN = '<unknown>'  # MUST MATCH `TOKEN_PATTERN`, so might need to be lowercase
MODEL_FILES_DIRECTORY = 'model_files'
TOKEN_PATTERN = r"(?u)(<?\b\w+\b>?)"  # Altered token pattern that contains < and > around the words


def transpose_dialog_acts(dialog_acts: List[Tuple[str, str]]) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """
    This will transform the `dialog_acts` from a list of (X, y) pairs:
    ```
    [ (CLASS_A, PHRASE_1), (CLASS_B, PHRASE_2), (CLASS_C, PHRASE_3), ... ]
    ```
    into a `tuple` of X values and a `tuple` of y values:
    ```
    (PHRASE_1, PHRASE_2, PHRASE_3, ... ), ( CLASS_A, CLASS_B, CLASS_C, ... )
    ```

    This can be useful to format the data correctly into model inputs. 

    :param List[Tuple[str, sr]] dialog_acts: The dialog acts in the list-of-tuples-format.
    :returns: Two tuples, one for phrases (X) and one for phrases (y).
    :rtype: Tuple[Tuple[str, ...], Tuple[str, ...]]
    """
    # Transpose dialog acts so we get <classes, phrases> (y, X; but in text still)
    classes: Tuple[str, ...]
    phrases: Tuple[str, ...]
    classes, phrases = tuple(zip(*dialog_acts))

    return phrases, classes


def fit_count_vectorizer(dialog_phrases: Tuple[str, ...], dialog_classes: Tuple[str, ...]) -> CountVectorizer:
    """
    Trains a `CountVectorizer` on the passed phrases (corpus) and classes (y/target), will return the 'trained'
    object for future use. The `CountVectorizer` saves the word frequency for each word.

    :param Tuple[str, ...] dialog_phrases: All the dialog phrases in the training data.
    :param Tuple[str, ...] dialog_classes: All the dialog act classes in the training data for the respective `dialog_phrases`.
    :returns: A trained CountVectorizer object.
    :rtype: sklearn.feature_extraction.text.CountVectorizer
    :raises ValueError: When `dialog_phrases` and `dialog_classes` do not have the same length.
    """

    if len(dialog_phrases) != len(dialog_classes):
        raise ValueError("`dialog_phrases` and `dialog_classes` must have the same length.")

    count_vec_kwargs: Dict[str, Any] = { 'token_pattern': TOKEN_PATTERN }
    count_vec: CountVectorizer = CountVectorizer(**count_vec_kwargs) # type: ignore
    # This will fit the word frequences to the corpi (phrases) 
    count_vec.fit(raw_documents=dialog_phrases, y=dialog_classes)  # type: ignore

    # Add an unknown 'token' to the vocab
    vocab: Dict[str, int] = count_vec.vocabulary_
    if len(vocab) == 0 :
        raise ValueError("Passed `dialog_phrases` is of length 0 or do not contain text.")
    vocab[UNK_TOKEN] = len(vocab)

    # Reinitialize the count_vec with the unk vocab
    count_vec = CountVectorizer(vocabulary=vocab, **count_vec_kwargs)  # type: ignore
    return count_vec


# @TODO: Look into making this function more efficient along with `get_embeddings`
def _replace_unknowns(tokenizer: Callable, vocabulary: Dict[str, int], texts: Iterable[str]) -> List[str]:
    """
    Replaces unknown tokens from text with the value associated with `UNK_TOKEN`.
    This is a weakly private function as there is no practical use for this function outside of `get_embeddings`.

    :param Callable tokeziner: The tokenzier of the associated CountVectorizer 
        (can be generated with `CountVectorizer.build_analyzer()`)
    :param Dict[str, int] vocabulary: The vocabulary of the CountVectorizer object.
        (can be retrieved with `CountVectorizer.vocabulary`)
    :param Iterable[str] texts: The texts in which the unknown words will to be replaced. 
    :returns: The texts with unknown vocabulary replaced with `UNK_TOKEN` value.
    :rtype: List[str]
    """
    processed_texts: List[str] = []
    
    for text in texts:
        tokens: List[str] = tokenizer(text)
        new_tokens: List[str] = [(token if token in vocabulary else UNK_TOKEN) for token in tokens]
        new_text = ' '.join(new_tokens)
        processed_texts.append(new_text)

    return processed_texts


def get_embeddings(count_vectorizer: CountVectorizer, texts: List[str]) -> spmatrix:
    """
    Extracts the bag of words embeddings from the texts passed.

    :param CountVectorizer count_vectorizer: The vectorizer object that contains all of the trained data.
    :param List[str] texts: The texts that need to be embedded.
    :returns: A sparse matrix with the word embeddings. This can be turned into a normal array with `.toarray()`.
    :rtype: scipy.sparse.spmatrix
    :raises: 
    """
    if isinstance(texts, str):
        raise TypeError("Argument `texts` must be an interable of str objects, not a `str` object")

    tokenizer: Callable = count_vectorizer.build_analyzer()
    vocabulary = count_vectorizer.vocabulary  # type: ignore

    fixed_texts: List[str] = _replace_unknowns(
        tokenizer=tokenizer,
        vocabulary=vocabulary,
        texts=texts)

    embeddings = count_vectorizer.transform(fixed_texts)
    return embeddings


if __name__ == '__main__':
    I = -1

    # Original file name is `dailog_acts.dat`
    file_path = 'data/dialog_acts.dat'
    dat_lines = parser.read_text_file_lines(file_path)
    dialog_acts = parser.parse_dstc_dat_file(dat_lines[:I])

    # Train vectorizer
    phrases, classes = transpose_dialog_acts(dialog_acts)
    count_vec = fit_count_vectorizer(phrases, classes)
    
    # EXAMPLE: Save the object 
    count_vec_file_name: str = "count_vec.joblib"
    count_vec_path: str = os.path.join(MODEL_FILES_DIRECTORY, count_vec_file_name)
    joblib.dump(count_vec, count_vec_path)

    # EXAMPLE: Load the object
    count_vec_loaded = joblib.load(count_vec_path)

    texts = ["Hello there user, how are you?",]
    texts = list(map(parser.sanitize_phrase, texts)) 

    print('phrase(s):', texts, sep='\n\t')

    embeddings = get_embeddings(count_vec, texts)
    print('\nspmatrix:', embeddings, sep='\n\t')

    # Reverse engineer the passed tokens.
    word_columns = embeddings.tocoo().col  # type: ignore
    vocab_t = {v: k for k, v in count_vec.vocabulary_.items()}
    # Display in set to make it clear that it's unordered and non-duplicative
    print('\nrev-engineered tokens:', {vocab_t[widx] for widx in word_columns},
          sep='\n\t') 
