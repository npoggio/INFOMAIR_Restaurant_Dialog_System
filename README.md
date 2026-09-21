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

