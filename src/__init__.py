from .enums.models import Models
from .models import support_vector_machine_model as svm
from .models import logistic_regression_model as lr
from .utils.document_term import get_embeddings

PROGRAM = 'Restaurant Dialog System'
DESCRIPTION = '''A dialog system for choosing a restaurant.
Created by W. Boersma, J.O. Ceulemans, M.A.I. Lalta & N.D. Poggio.'''

MODEL_NAMES = {
    'rb': Models.RULE_BASED,
    'svm_bow': Models.SUPPORT_VECTOR_MACHINE_BOW,
    'lr_bow': Models.LOGISTIC_REGRESSION_BOW,
    'svm_trans': Models.SUPPORT_VECTOR_MACHINE_BERT,
    'lr_trans': Models.LOGISTIC_REGRESSION_BERT,
}

MODELS_TRAINING = {
    Models.RULE_BASED: 
        None,
    Models.SUPPORT_VECTOR_MACHINE_BOW: 
        lambda kwargs: svm.train_support_vector_machine(**kwargs, embed_func=get_embeddings),
    Models.LOGISTIC_REGRESSION_BOW: 
        lambda kwargs: lr.train_logistic_regression(**kwargs, embed_func=get_embeddings),
    Models.SUPPORT_VECTOR_MACHINE_BERT:                                    # TODO: CHANGE TO BERT!
        lambda kwargs: svm.train_support_vector_machine(**kwargs, embed_func=get_embeddings),
    Models.LOGISTIC_REGRESSION_BERT:                                   # TODO: CHANGE TO BERT!
        lambda kwargs: lr.train_logistic_regression(**kwargs, embed_func=get_embeddings),
}