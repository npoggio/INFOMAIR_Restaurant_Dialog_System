from typing import Dict, Any
import argparse
import sys
import src.models.support_vector_machine_model as svm
import src.models.logistic_regression_model as lr
import src.models.rule_based_baseline as rb
from src.enums.models import Models
from src import PROGRAM, DESCRIPTION, MODEL_NAMES, MODELS_TRAINING

ALLOWED_MODELS = [model_name for model_name, model in MODEL_NAMES.items() if MODELS_TRAINING[model]]


def train_arg_parser() -> Dict[str, Any]:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIPTION,
    )

    # Model
    parser.add_argument('-m', '--model', 
                        type=str, required=True, help='Model types', choices=ALLOWED_MODELS)
    parser.add_argument('-i', '--input_path', 
                        type=str, required=True)
    parser.add_argument('-o', '--output_path', 
                        type=str, required=True)
    parser.add_argument('-r', '--random_state', 
                        type=int, required=True)
    parser.add_argument('-g', '--grouped_split', 
                        action='store_true', help='Whether to keep all same X in the train/split sections')
    parser.add_argument('--evaluate',
                        action='store_true', help='Whether to evaluate the train input')

    args = sys.argv[1:]
    namesp = parser.parse_args(args=args)
    return namesp.__dict__


def train(model: Models, input_path: str, evaluate: bool,
          output_path: str, random_state: int, grouped_split: bool):

    training_func = MODELS_TRAINING[model]
    training_kwargs = {
        'data_path': input_path,
        'model_path': output_path,
        'random_state': random_state,
        'grouped_split': grouped_split,
        'evaluate': evaluate
    }

    training_func(training_kwargs)


if __name__ == '__main__':
    kwargs = train_arg_parser()

    model_name = kwargs['model']
    output_path = kwargs['output_path']
    output_path = output_path.removesuffix('.joblib') + '.joblib'

    kwargs['model'] = MODEL_NAMES[model_name]
    kwargs['output_path'] = output_path

    train(**kwargs)