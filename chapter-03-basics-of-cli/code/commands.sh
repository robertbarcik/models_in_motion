#!/bin/bash
# ============================================================
# Chapter 1: Basics of Command Line
# All commands from this chapter, organized by section.
# ============================================================


# ============================================================
# Getting started with the terminal
# ============================================================

echo "Hi Robert"

# Variables
myvar=10
echo myvar
echo "myvar"
echo $myvar
echo "$myvar"

# Clear the screen
clear


# ============================================================
# Navigation
# ============================================================

cd Desktop
cd chapter_1_basics_of_CLI
pwd
ls

# Move one level up
cd ..

# Create a new folder
mkdir my_experiments
ls

# Navigate back
cd chapter_1_basics_of_CLI

# Create an empty file
touch my-file.txt
ls

# Edit a file with nano
nano my-file.txt
# Type: Wohooo! Hi CLI!
# Save: Ctrl + O, Enter, Ctrl + X


# ============================================================
# Viewing file contents
# ============================================================

# Display entire file
cat my-file.txt

# Display multiple files
cat chapter_1_basics_of_CLI/notes.txt README.txt

# Show first 10 lines (default)
head materials/sales_data.csv

# Show first 5 lines
head -n 5 materials/sales_data.csv

# Show last lines
tail materials/app.log


# ============================================================
# Combining commands
# ============================================================

# Piping: pass output of one command to another
cat materials/customers.txt | head -n 3

# Search for a pattern with grep
cat materials/errors.log | grep "Division by zero"

# Chain multiple pipes: search and count
cat materials/errors.log | grep "Division by zero" | wc -l

# Redirect output to a file (overwrites)
head -n 5 materials/sales_data.csv > sales_preview.csv

# Append to a file
echo "--- End of preview ---" >> sales_preview.csv


# ============================================================
# File operations
# ============================================================

# Copy a file
cp sales_data.csv sales_data_backup.csv
ls

# Create a directory and copy into it
mkdir backups
cp sales_data_backup.csv backups/sales_data_backup.csv

# Copy with overwrite confirmation
cp -i sales_data_backup.csv backups/sales_data_backup.csv

# Rename a directory (mv in same location = rename)
mv backups/ datasets/
ls

# Move a file to another directory with a new name
mv app.log datasets/app_2024_01_15.log

# Remove a file (no undo!)
rm notes.txt

# Remove an empty directory
rmdir my_experiments

# Remove a directory with contents (recursive)
rm -r datasets


# ============================================================
# Running a program from the command line
# ============================================================

# Check Python version
python3 --version

# Create a script with nano
nano simple_print_program.py
# Type: print("Hi Robert! How are you today?")
# Save: Ctrl + O, Enter, Ctrl + X

# Run the script
python simple_print_program.py


# ============================================================
# Making scripts directly executable
# ============================================================

# Add shebang line to the script (first line: #!/usr/bin/env python3)
# Then make it executable:
chmod +x simple_print_program.py

# Run directly without typing python
./simple_print_program.py


# ============================================================
# Passing arguments - Approach 1: sys module
# ============================================================

# Create the helper module
nano my_module.py
# Paste the greet function from the chapter

# Create the sys_args script
nano sys_args_program.py
# Paste the code from the chapter

# Run with arguments
python sys_args_program.py Robert --shout 3


# ============================================================
# Passing arguments - Approach 2: argparse module
# ============================================================

# Create the argparse script
nano argparse_program.py
# Paste the code from the chapter

# Run with positional and optional arguments
python argparse_program.py Robert
python argparse_program.py Robert --shout --lines 2
python argparse_program.py Robert --lines 2 --shout

# Show auto-generated help
python argparse_program.py --help

# Create the positional example script
nano positional_example.py
# Paste the code from the chapter

# Various ways to call it
python positional_example.py Robert
python positional_example.py Robert --greeting Hi
python positional_example.py Robert -g Hey
