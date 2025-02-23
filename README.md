# drupal-cs-cursor
A script that scrapes Drupal Coding Standards and create cursor rules out of it.

# Setup

## Virtual env and packages.

### Virtual environment

1. Create virtual environment, make sure your in the project directory 

```
python3 -m venv .venv
```

2. Activate the virtual environment

```
source .venv/bin/activate
```


3. Verify that it uses the .venv environment

```
which python
```

Should output a filepath that includes the .venv (this to ensure we're not messing with the default python)

This to deactivate (don't do that now ;)):
```
deactivate
```

Prepare pip for the virtual env.

```
python3 -m pip install --upgrade pip
python3 -m pip --version
```

4. Install packages

In the requirements.txt we have all the packages we need

```
run pip install -r requirements.txt
```

# Run the script

```
python3 drupal_standards_to_mdc.py

```
