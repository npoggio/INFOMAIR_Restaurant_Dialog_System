import os

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
)
from sklearn.model_selection import train_test_split

import parser
from document_term import (
    MODEL_FILES_DIRECTORY,
    fit_count_vectorizer,
    get_embeddings,
    transpose_dialog_acts,
)


DATA_PATH = "src/dialog_acts.dat"
MODEL_NAME = "logistic_regression_bow.joblib"
TEST_SIZE = 0.15
RANDOM_STATE = 12345


def train_logistic_regression():
    # Read and parse the dataset
    lines = parser.read_text_file_lines(DATA_PATH)
    dialog_acts = parser.parse_dstc_dat_file(lines)

    # Separate utterances and labels
    phrases, classes = transpose_dialog_acts(dialog_acts)

    # Split raw text into 85% training and 15% testing
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        phrases,
        classes,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=classes,
    )

    # Learn the bag-of-words vocabulary from training text only
    vectorizer = fit_count_vectorizer(
        dialog_phrases=X_train_text,
        dialog_classes=y_train,
    )

    # Convert raw text into numerical feature vectors
    X_train = get_embeddings(
        count_vectorizer=vectorizer,
        texts=list(X_train_text),
    )

    X_test = get_embeddings(
        count_vectorizer=vectorizer,
        texts=list(X_test_text),
    )

    # Create and train Logistic Regression
    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    classifier.fit(X_train, y_train)

    # Evaluate it
    predictions = classifier.predict(X_test)

    print(
        "Accuracy:",
        accuracy_score(y_test, predictions),
    )

    print(
        "Balanced accuracy:",
        balanced_accuracy_score(y_test, predictions),
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # Save the vectorizer and classifier together
    os.makedirs(MODEL_FILES_DIRECTORY, exist_ok=True)

    model_bundle = {
        "vectorizer": vectorizer,
        "classifier": classifier,
    }

    model_path = os.path.join(
        MODEL_FILES_DIRECTORY,
        MODEL_NAME,
    )

    joblib.dump(model_bundle, model_path)

    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    train_logistic_regression()