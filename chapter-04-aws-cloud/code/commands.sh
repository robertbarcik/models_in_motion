#!/bin/bash
# ============================================================
# Chapter 4: Basics of AWS Cloud
# All commands from this chapter, organized by section.
# Most of this chapter involves the AWS Console (GUI).
# Below are the CLI commands used in the demos.
# ============================================================


# ============================================================
# S3 demo: Downloading a file from a public S3 bucket
# ============================================================

curl https://<your-bucket-name>.s3.<your-region>.amazonaws.com/Demo_notebook.ipynb --output downloaded-notebook.ipynb


# ============================================================
# EC2 demo: Connecting to an instance via SSH
# ============================================================

# Restrict permissions on your private key file
chmod 400 <your-key-pair-name>.pem

# Connect to your EC2 instance
ssh -i "YourPrivateKey.pem" username@public-IP


# ============================================================
# EC2 demo: Installing Miniconda on the instance
# ============================================================

# Download Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Run the installer
sh ./Miniconda3-latest-Linux-x86_64.sh

# Replace current shell session
exec bash

# Or reload shell configuration
source ~/.bashrc

# Verify conda installation
conda --version

# Initialize conda for bash
conda init bash

# Exit and reconnect to your instance, then:
conda create --name my_env python=3.11
conda activate my_env
conda install jupyterlab


# ============================================================
# EC2 demo: SSH tunnel for Jupyter access
# ============================================================

# General format:
ssh -L [PORT-on-your-machine]:[IP-jupyter-server-on-ec2]:[PORT-jupyter-server-on-ec2] [username]@[public IP of EC2] -i [path to private key]

# Example:
ssh -L 8888:127.0.0.1:8888 ubuntu@ec2-18-156-155-181.eu-central-1.compute.amazonaws.com -i "my-test-instance-key-pair.pem"

# Then in the original terminal (logged into EC2):
jupyter lab
