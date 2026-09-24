:: Make sure to activate the environment before using this
python -m src.train -m svm_bow -r 12345 -i data/dialog_acts.dat -o model_files/svm_bow --evaluate
python -m src.train -m svm_bow -r 12345 -i data/dialog_acts.dat -o model_files/svm_bow_g -g --evaluate
python -m src.train -m svm_bert -r 12345 -i data/dialog_acts.dat -o model_files/svm_bert --evaluate
python -m src.train -m svm_bert -r 12345 -i data/dialog_acts.dat -o model_files/svm_bert_g -g --evaluate
python -m src.train -m lr_bow -r 12345 -i data/dialog_acts.dat -o model_files/lr_bow --evaluate
python -m src.train -m lr_bow -r 12345 -i data/dialog_acts.dat -o model_files/lr_bow_g -g --evaluate
python -m src.train -m lr_bert -r 12345 -i data/dialog_acts.dat -o model_files/lr_bert --evaluate
python -m src.train -m lr_bert -r 12345 -i data/dialog_acts.dat -o model_files/lr_bert_g -g --evaluate