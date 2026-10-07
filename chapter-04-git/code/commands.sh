#!/bin/bash
# ============================================================
# Chapter 2: Versioning with Git
# All commands from this chapter, organized by section.
# ============================================================


# ============================================================
# Our first repository
# ============================================================

# Install Git (choose your OS)
# macOS:    brew install git
# Ubuntu:   sudo apt install git

# Verify installation
git --version

# Initialize a new repository
git init

# Set main as default branch name (one-time global setting)
git config --global init.defaultBranch main

# Rename current branch to main
git branch -m main

# Check repository status
git status

# Create a file
touch nothing.txt

# Check status again (nothing.txt is untracked)
git status

# Stage a specific file
git add nothing.txt

# Or stage all changes
git add .

# Check status (file is now staged)
git status

# Commit staged changes
git commit -m "Created our first file"

# Edit the file
nano nothing.txt
# Type some text, then Ctrl + O, Enter, Ctrl + X

# Stage and commit the changes
git add .
git commit -m "Added content to nothing.txt"

# View commit history
git log


# ============================================================
# Pushing to GitHub
# ============================================================

# Configure your identity
git config --global user.name "Your Name"
git config --global user.email "youremail@example.com"

# Authenticate with GitHub CLI
gh auth login

# Link local repo to remote and push
git remote add origin https://github.com/<your-username>/<your-repository-name>.git
git push -u origin main


# ============================================================
# What should NOT be in a repository (.gitignore)
# ============================================================

# Create .gitignore file
nano .gitignore
# Add patterns for files to ignore (archives, data, venv, etc.)

# Install nbstripout (strips Jupyter notebook outputs on commit)
pip install nbstripout
nbstripout --install

# Set up nbstripout globally
nbstripout --install --global

# Create global gitattributes file
nano ~/.gitattributes_global
# Add: *.ipynb filter=nbstripout

# Tell Git where to find it
git config --global core.attributesfile '~/.gitattributes_global'


# ============================================================
# Creating a repository for practice
# ============================================================

mkdir git_practice
cd git_practice
git init

echo "Hello, this is my practice repository" > practice.txt

git add practice.txt
git commit -m "Initial commit - added practice.txt"

# Create repo on GitHub, then link and push
git remote add origin https://github.com/<your-username>/git_practice.git
git push -u origin main


# ============================================================
# Cloning a repository
# ============================================================

cd ~
git clone https://github.com/<your-username>/git_practice.git git_practice_clone
cd git_practice_clone

ls
cat practice.txt
git log

# Verify remote connection
git remote -v


# ============================================================
# Making and pushing changes
# ============================================================

nano practice.txt
# Add a second line, then save and exit

git status
git diff

git add practice.txt
git commit -m "Added second line from cloned repository"
git push origin main


# ============================================================
# Pulling changes from remote
# ============================================================

cd ~/git_practice
cat practice.txt

git pull origin main
cat practice.txt


# ============================================================
# Git branches
# ============================================================

cd ~/git_practice
git switch main

# Create a new branch
git branch feature/add-greeting

# Switch to the new branch
git switch feature/add-greeting

# Or create and switch in one step
git switch -b feature/add-greeting

# List all branches
git branch

# Create a file on the feature branch
echo "Hello! Welcome to my practice repository." > greeting.txt
git add greeting.txt
git commit -m "Added greeting.txt with welcome message"


# ============================================================
# Merging branches
# ============================================================

# Switch back to main
git switch main

# Merge feature branch into main
git merge feature/add-greeting

# Push updated main
git push origin main


# ============================================================
# Deleting and renaming branches
# ============================================================

# Delete a merged branch (safe)
git branch -d feature/add-greeting

# Delete an unmerged branch (force)
git branch -D branch-name

# Rename current branch
git switch branch-to-rename
git branch -m new-branch-name


# ============================================================
# Restoring and stashing
# ============================================================

# Revert a file to its last committed state
git restore "file_to_be_reverted"

# Stash current changes
git stash

# List stashes
git stash list

# Switch to main and fix a bug
git switch main
git add .
git commit -m "Fixed a critical bug"
git push origin main

# Go back to feature branch and restore stashed changes
# Option 1: apply and remove from stash
git stash pop

# Option 2: apply but keep in stash
git stash apply
