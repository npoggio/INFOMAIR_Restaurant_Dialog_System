import os
from typing import Callable

import joblib
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    classification_report,
)

from src.utils import parser
from src.utils.data_split import split_data
from src.utils.model_io import save_model, load_model, write_performance
from src.utils.document_term import (
    MODEL_FILES_DIRECTORY,
    fit_count_vectorizer,
    get_embeddings,
    transpose_dialog_acts,
)

#DATA_PATH = 
#MODEL_NAME = "svm_bow.joblib"
#RANDOM_STATE = 12345

def run_loaded_support_vector_machine(model_path, **kwargs):
    classifier, vectorizer = load_model(model_path)
    return run_support_vector_machine(classifier, vectorizer, **kwargs)


def run_support_vector_machine(classifier, vectorizer, embed_func, phrases):
    X = embed_func(
        count_vectorizer=vectorizer,
        texts=phrases,
    )
    predictions = classifier.predict(X)
    return predictions


def train_support_vector_machine(data_path: str, model_path: str, random_state: int, 
                                 embed_func: Callable, grouped_split: bool = False, evaluate: bool = True):
    # Read and parse the dataset
    lines = parser.read_text_file_lines(data_path)
    dialog_acts = parser.parse_dstc_dat_file(lines)

    # Separate utterances and labels
    phrases, classes = transpose_dialog_acts(dialog_acts)

    # Split the raw text into training and testing data
    data = split_data(
        X=phrases,
        y=classes,
        test_size=0.15,
        random_state=random_state,
        grouped=grouped_split,
    )

    # Learn the bag-of-words vocabulary from training text only
    vectorizer = fit_count_vectorizer(
        dialog_phrases=data.X_train,  # type: ignore
        dialog_classes=data.y_train,  # type: ignore
    )

    # Convert raw text into numerical feature vectors
    X_train = embed_func(
        count_vectorizer=vectorizer,
        texts=list(data.X_train),
    )

    X_test = embed_func(
        count_vectorizer=vectorizer,
        texts=list(data.X_test),
    )

    # Create and train Logistic Regression
    classifier = LinearSVC(
        penalty = "l2",
        loss = 'squared_hinge',
        dual = True,
        tol = 0.0001,
        C = 1,
        multi_class = "ovr",
        fit_intercept = True,
        intercept_scaling = 1,
        class_weight=None,
        random_state=random_state,
        max_iter=1000,
    )

    classifier.fit(X_train, data.y_train)

    # Save the vectorizer and classifier together
    model_dir: str = os.path.abspath(os.path.join(model_path, '..'))
    os.makedirs(model_dir, exist_ok=True)
    save_model(model_path, classifier=classifier, vectorizer=vectorizer)
    print(f"Saved model to {model_path}")
    
    if evaluate:
        # Evaluate the model
        predictions = classifier.predict(X_test)
        file_name = model_path.removesuffix('.joblib') + '_perf_train.json'
        report = write_performance(data.y_test, predictions, file_name)
        print(report)

    return classifier, vectorizer


if __name__ == "__main__":
    data_path = "data/dialog_acts.dat"
    model_path = os.path.join(MODEL_FILES_DIRECTORY, 'svm_bow.joblib')
    random_state = 12345

    train_support_vector_machine(
        data_path = data_path,
        model_path = model_path,
        random_state = random_state,
        embed_func = get_embeddings
    )