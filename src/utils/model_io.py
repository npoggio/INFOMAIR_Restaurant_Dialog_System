from typing import Any, Tuple
import joblib
import os
import json
from sklearn.metrics import classification_report

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


def write_performance(y_true, y_pred, path) -> str:
    class_rep_kwargs = dict(
        y_true=y_true,
        y_pred=y_pred,
        zero_division=0,
        digits=3,
    )

    class_rep = classification_report(**class_rep_kwargs, output_dict=True) # type: ignore

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(class_rep, file, indent=4)

    return (classification_report(**class_rep_kwargs)) # type: ignore
    

if __name__ == '__main__':
    out = load_model('model_files/svm_bow.joblib')
    print(out)