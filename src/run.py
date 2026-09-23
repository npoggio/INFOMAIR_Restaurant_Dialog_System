from typing import Dict, Any
import argparse
import sys
import src.models.support_vector_machine_model as svm
import src.models.logistic_regression_model as lr
import src.models.rule_based_baseline as rb
import src.utils.parser as parser
import src.utils.document_term as document_term
from src.enums.models import Models
from src import PROGRAM, DESCRIPTION, MODEL_NAMES, MODEL_RUNNING

ALLOWED_MODELS = list(MODEL_NAMES.keys())


def run_arg_parser() -> Dict[str, Any]:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIPTION,
    )

    # Model
    parser.add_argument('-m', '--model', 
                        type=str, required=True, help='Model types', choices=ALLOWED_MODELS)
    parser.add_argument('-i', '--input_path', 
                        type=str, help='The path to the model (with exception of `rb`)')
    parser.add_argument('-p', '--phrases', 
                        type=str, nargs='+', help='Phrases to test surrounded with ""')
    parser.add_argument('-d', '--data_path', 
                        type=str, help="The path to a .dat or .txt file to run")

    args = sys.argv[1:]
    namesp = parser.parse_args(args=args)
    return namesp.__dict__


def run_file(model: Models, input_path: str, data_path: str, **kwargs):
    running_func = MODEL_RUNNING[model]

    # Read and parse the dataset
    lines = parser.read_text_file_lines(data_path)

    if data_path.endswith('.dat'):
        dialog_acts = parser.parse_dstc_dat_file(lines)
        phrases, classes = document_term.transpose_dialog_acts(dialog_acts)
    else:
        phrases = lines
        
    running_kwargs = {
        'model_path': input_path,
        'phrases': phrases,
    }

    return running_func(running_kwargs)

def run_str(model: Models, input_path: str, phrases: list, **kwargs):
    running_func = MODEL_RUNNING[model]
    running_kwargs = {
        'model_path': input_path,
        'phrases': phrases,
    }

    return running_func(running_kwargs)


if __name__ == '__main__':
    kwargs = run_arg_parser()

    has_phrases = kwargs['phrases'] is not None
    has_data_path = kwargs['data_path'] is not None

    model_name = kwargs['model']
    input_path = kwargs['input_path']
    #input_path = '' if input_path is None else input_path
    input_path = input_path.removesuffix('.joblib') + '.joblib'

    kwargs['model'] = MODEL_NAMES[model_name]
    kwargs['input_path'] = input_path

    if has_phrases and not has_data_path:
        out = run_str(**kwargs)
    elif has_data_path and not has_phrases:
        out = run_file(**kwargs)
    else:
        raise ValueError("You mast pass either `--phrases` or `--data_path`. Not both, nor neither")

    print(out)