from typing import Any, Tuple
import joblib
import os


def save_model(file_path, classifier, vectorizer):
    model_bundle = {
        "vectorizer": vectorizer,
        "classifier": classifier,
    }

    joblib.dump(model_bundle, file_path)


def load_model(file_path) -> Tuple[Any, Any]:
    """Loads classifer and vectorizer from a model file"""
    model = joblib.load(file_path)

    if not 'classifier' in model:
        raise ValueError("Passed saved model does not contain a classifier")
    if not 'vectorizer' in model:
        raise ValueError("Passed saved model does not contain a vectorizer")

    classifier = model['classifier']
    vectorizer = model['vectorizer']

    return classifier, vectorizer


if __name__ == '__main__':
    out = load_model('model_files/support_vector_machine_bow.joblib')
    print(out)