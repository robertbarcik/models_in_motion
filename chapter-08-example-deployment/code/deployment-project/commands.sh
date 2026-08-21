#!/bin/bash
# ============================================================
# Chapter 8: Example Deployment of ML Model
# Commands for the deployment workflow.
# ============================================================


# ============================================================
# Environment setup
# ============================================================

python3 -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt


# ============================================================
# Training (run in Jupyter or as script)
# ============================================================

# Open Jupyter
jupyter notebook

# Or run training script directly
python model_training.py


# ============================================================
# Creating predict.py - compile requirements
# ============================================================

pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt


# ============================================================
# Test 2: Run Flask app locally
# ============================================================

# Terminal 1: start the server
python predict.py

# Terminal 2: test it
python test_predict.py


# ============================================================
# Test 3: Build Docker image
# ============================================================

docker build -t wine-quality-model .
docker images


# ============================================================
# AWS CLI setup
# ============================================================

aws configure
aws ec2 describe-instances

# Install Elastic Beanstalk CLI
pip install awsebcli
eb --version


# ============================================================
# Initialize Elastic Beanstalk
# ============================================================

eb init -p "Docker running on 64bit Amazon Linux 2" wine-quality-serving


# ============================================================
# Test 4: Local EB run
# ============================================================

eb local run --port 9696


# ============================================================
# Deploy to AWS
# ============================================================

eb create wine-quality-model-environment


# ============================================================
# Cleanup
# ============================================================

eb terminate wine-quality-model-environment
