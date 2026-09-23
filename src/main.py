import argparse
import src.models.support_vector_machine_model as svm
import src.models.logistic_regression_model as lr
import src.models.rule_based_baseline as rb
from src.enums.models import Models


PROGRAM = 'Restaurant Dialog System'
DESCRIPTION = '''A dialog system for choosing a restaurant.
Created by W. Boersma, J.O. Ceulemans, M.A.I. Lalta & N.D. Poggio.'''

MODELS = {
    'svm': Models.SUPPORT_VECTOR_MACHINE,
    'support_vector_machine': Models.SUPPORT_VECTOR_MACHINE,
    'rb': Models.RULE_BASED,
    'rule_based': Models.RULE_BASED,
    'lr': Models.LOGISTIC_REGRESSION,
    'logistic_regression': Models.LOGISTIC_REGRESSION
}


def cli_arg_parser():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIPTION,
    )

    # Create model
    parser.add_argument('-c', '--create', action='store_true')
    # Run inference
    parser.add_argument('-r', '--run', action='store_true')

    # Model
    parser.add_argument('-m', '--model', type=str)

    namesp = parser.parse_args()
    # Either create or run needs to be active
    
    if not (namesp.create ^ namesp.run):
        raise ValueError("Either `--create` or `--run` needs to be `True`, not neither nor both.") 

    return namesp


def main(create: bool, 
         run: bool,
         model: str):
    ...

if __name__ == '__main__':
    namespace = cli_arg_parser()
    print(namespace)