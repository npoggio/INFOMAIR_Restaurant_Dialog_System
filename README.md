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