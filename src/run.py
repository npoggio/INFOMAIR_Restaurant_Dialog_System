from typing import Dict, Any
import argparse
import sys
import src.models.support_vector_machine_model as svm
import src.models.logistic_regression_model as lr
import src.models.rule_based_baseline as rb
import src.utils.parser as parser
import src.utils.data_split as data_split
from src.utils.model_io import write_performance
import src.utils.document_term as document_term
from src.enums.models import Models
from src import PROGRAM, DESCRIPTION, MODEL_NAMES, MODEL_RUNNING, DO_LOWER, REMOVE_APOSTRAPHES

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
    parser.add_argument('--interactive', 
                        action='store_true', help="Enable flexable inputs")
    parser.add_argument('--evaluate', 
                        action='store_true', help="Write an evauation to the input path, altered to be a txt file")
    parser.add_argument('--test_split', 
                        type=float, help="The testsplit of the .dat file to run (only for --evaluate)", default=1.0)
    parser.add_argument('--tts_seed', 
                        type=int, help="The split for the test (only for --evaluate)")
    parser.add_argument('-g', '--grouped_split', 
                        action='store_true', help='Whether to keep all same X in the train/split sections (only for --evaluate)')    

    args = sys.argv[1:]
    namesp = parser.parse_args(args=args)
    return namesp.__dict__


def run_file(model: Models, input_path: str, data_path: str, evaluate: bool, **kwargs):
    running_func = MODEL_RUNNING[model]

    # Read and parse the dataset
    lines = parser.read_text_file_lines(data_path)

    if data_path.endswith('.dat'):
        dialog_acts = parser.parse_dstc_dat_file(lines)
        phrases, classes = document_term.transpose_dialog_acts(dialog_acts)
    else:
        phrases = lines

    print(dict(
        X=phrases,
        y=classes,
        test_size=kwargs.get('test_split', 1.0),
        random_state=kwargs.get('tts_seed'),
        grouped=kwargs.get('grouped_split')
    ))

    if kwargs.get('test_split', 1.0) < 1.0:
        ds = data_split.split_data(
            X=phrases,
            y=classes,
            test_size=kwargs.get('test_split', 1.0),
            random_state=kwargs.get('tts_seed'),
            grouped=kwargs.get('grouped_split')
        )
        x_test, y_test = ds.X_test, ds.y_test
    else:
        x_test, y_test = phrases, classes

    phrases = [parser.sanitize_phrase(phrase) for phrase in x_test]
    running_kwargs = {
        'model_path': input_path,
        'phrases': phrases,
    }

    output = running_func(running_kwargs)

    if data_path.endswith('.dat'):
        path = (
            input_path
            .removesuffix('.joblib')  
            .removesuffix('/')  # For when people add / at the end
            .removesuffix('\\')
            + '_perf.json'
        )
        perf = write_performance(y_test, output, path)  # type: ignore
        print(perf)

    return output

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
    interactive = kwargs['interactive']

    model_name = kwargs['model']
    input_path = kwargs['input_path']
    input_path = 'model_files/rb' if input_path is None else input_path
    input_path = input_path.removesuffix('.joblib') + '.joblib'

    kwargs['model'] = MODEL_NAMES[model_name]
    kwargs['input_path'] = input_path

    if not interactive:
        if has_phrases and not has_data_path:
            out = run_str(**kwargs)
        elif has_data_path and not has_phrases:
            out = run_file(**kwargs)
        else:
            raise ValueError("You mast pass either `--phrases` or `--data_path`. Not both, nor neither")

        print(out)
    else:
        print(f'Interactive {model_name} UI. type QUIT to exit')
        while True:
            user_input = input("You: ")

            if user_input == 'QUIT':
                break

            kwargs['phrases'] = [user_input]
            out = run_str(**kwargs)
            print(out)