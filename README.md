# InfoMAIR
Super cool project about making a restuarent recommendaiton bot >:D


## Environment Setup

Create the Mamba environment in the MiniForge Prompt using:

```bash
mamba env create -f environment.yml
```

Activate the environment:

```bash
mamba activate infomair
```

If that doesn't work you might need to allow the console to run mamba commands with 

```bash
mamba shell init --shell powershell --root-prefix=~/.local/share/mamba
```

To deactivate the environment:

```bash
mamba deactivate
```


## Updating the Environment

When adding a new dependency, install it with Mamba:

```bash
mamba install <package-name>
```

Then add the package to the `dependencies` section of `environment.yml` and commit the change.

After pulling an updated `environment.yml`, update your existing environment with:

```bash
mamba env update -f environment.yml
```

## Data Insertion

The `dailog_acts.dat` (sic) file can be downloaded from [Brightspace](https://uu.brightspace.com/d2l/le/lessons/121884/topics/693121) and put into the [`data/`](data/) folder. 

__***NOTE!!!***__
The file is to be __RENAMED__ to `dialog_acts.dat` to fix a typo in the original file name. We recommend renaming it before putting it in the `data/` folder.

## Usage

### Training

There are two models that can be trained, the SVM and the LR models. Both have options for BERT and Bag of Words (BoW) features.
This is a list of all the models that can be trained, with example commands. 

| Model | Command | Embedding |
|-------|---------|-----------|
| Support Vector with BoW | `python -m src.train -m svm_bow -r 12345 -i data/dialog_acts.dat -o model_files/svm_bow --evaluate` | Bag of Words |
| Support Vector with BERT | `python -m src.train -m svm_bert -r 12345 -i data/dialog_acts.dat -o model_files/svm_bert --evaluate` | BERT |
| Logistic Regression with BoW | `python -m src.train -m lr_bow -r 12345 -i data/dialog_acts.dat -o model_files/lr_bow --evaluate` | Bag of Words |
| Logistic Regression with BERT | `python -m src.train -m lr_bert -r 12345 -i data/dialog_acts.dat -o model_files/lr_bert --evaluate` | BERT |

\**Note that SVM is Support Vector Machine with a Linear Kernel*

The Train-test split is automatically done with a 85-15 split, and the random seed can be set with the `-r` flag. The input file is specified with the `-i` flag, and the output file for the model files is specified with the `-o` flag, as the model will be exported to a .joblib file. The `-m` flag specifies the model to train, and the `-g` flag can be used to specify a grouped split instead of a random  split, which ensures that all duplicates of an utterance end up in the same split so no identical utterances leak between train and test. The default is a random split. Both splits are stratified by class. Lastly, the `--evaluate` flag can be used to evaluate the model on the test set after training and outputting the results to the console and a .json file in the model_files folder.

### Running

You can use the models with your phrases by running the following command, where the `-m` flag specifies the model to use (like above), the `-i` flag specifies the input model file, and the `-p` flag specifies the phrase to predict. The output will be a list of predictions for each phrase.

```bash
python -m src.run -m svm_bow -i model_files/svm_bow.joblib -p "Where is the best Italian place in my neighbourhood?"
> ['request']
```

You can also pass multiple sentences to the model, and it will return a list of predictions for each sentence.

```bash
python -m src.run -m svm_bow -i model_files/svm_bow.joblib -p "Where is the best Italian place in my neighbourhood?" "Thank you Goodbye :)"
> ['request' 'thankyou']
```

Alternatively, you can pass a file with phrases to the model, and it will return a list of predictions for each phrase in the file. The input file should be a .txt file with one phrase per line. Or a .dat file, which can be evaluated too. 

```bash
python -m src.run -m svm_bow -i model_files/svm_bow.joblib -f data/example_phrases.txt
> ['hello', 'inform']
```

Lastly, you can also have an interactive console where you can type in phrases and get predictions for each phrase. The console will exit when you type `exit` or `quit`. 

```bash
python -m src.run -m svm_bow -i model_files/svm_bow --interactive
> Interactive svm_bow UI. type QUIT to exit
> You: What is the best Italian restaurant near me?
> ['inform']
```

## Performance

| Model | Embedding | Accuracy | F1 Score | Random State |
|-------|-----------|----------|----------|--------------|