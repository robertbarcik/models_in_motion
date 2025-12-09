# Command Line Interface (CLI) - Hands-On Tutorial

Welcome to the CLI basics module! This README contains all the commands from the tutorial in order, so you can follow along step-by-step.

## Setup Instructions

1. **Create a working directory** on your computer
2. **Download the materials folder** with all practice files
3. **Open your terminal/command line**
4. **Navigate to this directory** using `cd`

## Tutorial Commands - Follow Along

### 1. Basic Commands

**Simple echo command:**
```bash
echo "Hi Robert"
```

**Clear your shell:**
```bash
clear
```

**Working with variables (note the $ symbol):**
```bash
# Variables are accessed with $ prefix
```

---

### 2. Navigation and Text Files

**List folders and files in current directory:**
```bash
ls
```

**Move to a desired folder:**
```bash
cd MyDirectoryName
```

**Move one level up:**
```bash
cd ..
```

**Create new folder:**
```bash
mkdir MyNewFolderName
```

**Print current working directory:**
```bash
pwd
```

**Create an empty text file:**
```bash
touch my-file.txt
```

**Open file in nano editor:**
```bash
nano my-file.txt
```

**View manual/documentation for a command:**
```bash
man ls
```

#### Viewing File Contents

**Display entire file contents:**
```bash
cat materials/customers.txt
```

**Display multiple files one after another:**
```bash
cat materials/notes.txt README.txt
```

**Show first 10 lines of a file:**
```bash
head materials/sales_data.csv
```

**Show first 5 lines (specify number):**
```bash
head -n 5 materials/sales_data.csv
```

**Show last few lines of a file:**
```bash
tail materials/app.log
```

#### File Operations

**Copy a file:**
```bash
cp materials/sales_data.csv materials/sales_data_backup.csv
```

**Create a new directory:**
```bash
mkdir -p data
```

**Copy with interactive mode (asks before overwriting):**
```bash
cp -i materials/sales_data_backup.csv data/sales_data_backup.csv
```

**Rename a directory:**
```bash
mv data/ datasets/
```

**Move and rename a file:**
```bash
mv materials/app.log datasets/app_2024_01_15.log
```

**Remove a single file:**
```bash
rm materials/notes.txt
```

**Remove an empty directory:**
```bash
rmdir old_directory/
```

**Remove entire folder with all contents (use with caution!):**
```bash
rm -r old_project/
```

---

### 3. Running a Program From a Command Line

**Create a simple Python script (simplePrintProgram.py):**
```python
print("Hi Robert! How are you today?")
```

**Run the Python script:**
```bash
python simplePrintProgram.py
```

**If python command not found (for zsh users):**
```bash
# Check available Python versions
brew search python

# Install Python (example)
brew install python-tk@3.9

# Add alias to zsh
echo "alias python=/usr/bin/python3" >> ~/.zshrc
```

**Check your Python version:**
```bash
python --version
```

#### Making Scripts Directly Executable

**Step 1: Add a shebang line to your script:**
```python
#!/usr/bin/env python3
# simplePrintProgram.py
# The shebang line above tells the system to use python3 to run this script

print("Hi Robert! How are you today?")
```

**Step 2: Make the file executable:**
```bash
# Add execute permission to the script
chmod +x simplePrintProgram.py
```

**Run directly without typing python:**
```bash
# Run directly - the shebang tells the system to use Python
./simplePrintProgram.py
```

#### Quick Inline Execution

**Execute Python code directly from the command line:**
```bash
# Execute a quick one-liner
python -c "print('Hello from the command line!')"

# Useful for quick checks, like verifying a package is installed
python -c "import numpy; print(numpy.__version__)"
```

---

### 4. Passing Arguments Into Our Program

#### Building a Simple Module

**Create myModule.py:**
```python
def greet(name, lines=1, loud=False):
    # Create the base greeting message using an f-string
    greeting_for_print = f'Hello {name}'

    # If loud mode is enabled, convert the greeting to uppercase
    if loud:
        greeting_for_print = greeting_for_print.upper()

    # Print the greeting the specified number of times
    for i in range(lines):
        print(greeting_for_print)
```

#### Approach 1: Using the sys Module

**Create sysArgsProgram.py:**
```python
import sys
from myModule import greet

args = sys.argv
print(f'Received {len(args)} arguments:')
for arg in args:
    print('  ' + arg)

loud = False
num = 1
for arg in args[1:]:
    if arg == '--shout':
        loud = True
    elif arg.isdigit():
        num = int(arg)

name = input("What's your name? ")
greet(name, num, loud)
```

**Run the program with arguments:**
```bash
python sysArgsProgram.py --shout 3
```

#### Approach 2: Using the argparse Module

**Create argparseProgram.py:**
```python
import argparse
from myModule import greet

# Create the parser and add a description
parser = argparse.ArgumentParser(description='An example program')

# Add named arguments
parser.add_argument('--shout', action="store_true", help="Print the greeting in uppercase")
parser.add_argument('--lines', type=int, default=1, help="Number of times to print the greeting")

# Parse the arguments
args = parser.parse_args()

# Print the parsed arguments (optional, for demonstration)
print(f'Lines: {args.lines}')
print(f'Shout: {args.shout}')

# Prompt for the user's name
name = input("What's your name? ")

# Call the greet function
greet(name, args.lines, args.shout)
```

**Run with argparse:**
```bash
python argparseProgram.py --shout --lines 2
```

**Arguments can be in any order:**
```bash
python argparseProgram.py --lines 2 --shout
```

**View auto-generated help documentation:**
```bash
python argparseProgram.py --help
```

#### Positional vs Optional Arguments Example

So far, we've used optional arguments (prefixed with --). Argparse also supports positional arguments - values that must be provided in a specific order. Let's create a script called `positionalExample.py` to demonstrate this:

```python
# positionalExample.py
# Demonstrates the difference between positional and optional arguments
# Positional arguments are required and must appear in a specific order
# Optional arguments (with --) can appear in any order and have defaults

import argparse

# Create the parser
parser = argparse.ArgumentParser(description='A greeting program with positional and optional arguments')

# Add a positional argument - no dashes means it's required and positional
parser.add_argument('name',
                    help="Name of the person to greet")

# Add an optional argument - dashes mean it's optional
# The '-g' is a short form, so users can type either --greeting or -g
parser.add_argument('--greeting', '-g',
                    default='Hello',
                    help="Greeting word to use")

# Parse the arguments
args = parser.parse_args()

# Use the arguments
print(f'{args.greeting}, {args.name}!')
```

**Usage:**
```bash
# Using the default greeting "Hello"
python positionalExample.py Robert

# Specifying a custom greeting with the full option name
python positionalExample.py Robert --greeting Hi

# Using the short form -g instead of --greeting
python positionalExample.py Robert -g Hey
```

#### Practical Examples for ML/Data Science

**Adjusting Hyperparameters:**
```bash
python train_model.py --learning_rate=0.01 --batch_size=32 --layers=3
```

**Choosing different algorithms:**
```bash
python train_model.py --algorithm=svm --kernel=linear
```

**Setting evaluation metrics:**
```bash
python evaluate_model.py --metric=f1_score
```

**Specifying dataset paths:**
```bash
python train_model.py --train_data=path/to/train_data_v2.csv --test_data=path/to/test_data_v2.csv
```

**Different data partitions:**
```bash
python train_model.py --use_validation=True --validation_data=path/to/validation.csv
```

**Define log directories:**
```bash
python train_model.py --log_dir=path/to/logs/
```

**Specify output directories:**
```bash
python process_data.py --output_dir=path/to/processed_data/
```

---

## Mock Data Files in materials/

- **customers.txt** - Customer database with IDs, names, and emails
- **sales_data.csv** - Sales transactions (date, product, quantity, price, region)
- **large_dataset.csv** - Larger sales dataset for practicing with big files
- **app.log** - Application logs with INFO, WARNING, ERROR, DEBUG messages
- **errors.log** - Error-only log file
- **notes.txt** - Project notes and TODO items

## Quick Tips

- **Tab completion:** Start typing and press Tab to autocomplete filenames
- **Command history:** Use up/down arrows to recall previous commands
- **Clear screen:** Type `clear` and press Enter
- **Get help:** Use `man <command>` to see the manual (e.g., `man ls`)
- **Careful with rm:** There's no undo - files are permanently deleted!

## Philosophy

> "Each thing should do one thing and do it well" - UNIX Philosophy

