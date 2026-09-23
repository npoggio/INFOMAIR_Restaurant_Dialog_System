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

The `dailog_acts.dat` file can be downloaded from [Brightspace](https://uu.brightspace.com/d2l/le/lessons/121884/topics/693121) and put into the [`data/`](data/) folder. 

__***NOTE!!!***__
The file is to be __RENAMED__ to `dialog_acts.dat` to fix a typo in the original file name. Make sure to rename it before putting it in the `data/` folder.

## Usage

### Training

There are two models that can be trained, the SVM and the LR models. Both have options for BERT and Bag of Words (BoW) features.

This is a list of all the models that can be trained, with example commands. 

| Model | Command | Embedding |
|-------|---------|-----------|
| Support Vector with BoW | `python -m src.train -m svm_bow -r 12345 -i data/dialog_acts.dat -o model_files/svm_bow` | Bag of Words |
| Support Vector with BERT | `python -m src.train -m svm_bert -r 12345 -i data/dialog_acts.dat -o model_files/svm_bert` | BERT |
| Logistic Regression with BoW | `python -m src.train -m lr_bow -r 12345 -i data/dialog_acts.dat -o model_files/lr_bow` | Bag of Words |
| Logistic Regression with BERT | `python -m src.train -m lr_bert -r 12345 -i data/dialog_acts.dat -o model_files/lr_bert` | BERT |

\**Note that SVM is Support Vector Machine with a Linear Kernel*