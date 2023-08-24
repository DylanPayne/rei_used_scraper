#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Now you can use $SCRIPT_DIR to build relative paths to other files or directories

# For example, if you want to refer to the 'venv' directory that's one level up
VENV_DIR="$SCRIPT_DIR/../venv"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Path to the Python interpreter inside the virtual environment
PYTHON_INTERPRETER="$VENV_DIR/bin/python3"

# Path to the Python script you want to run, assuming it's one level up from the script's location
PYTHON_SCRIPT="$SCRIPT_DIR/../rei_sweep_all.py"

# Run the Python script using the Python interpreter from the virtual environment
"$PYTHON_INTERPRETER" "$PYTHON_SCRIPT"