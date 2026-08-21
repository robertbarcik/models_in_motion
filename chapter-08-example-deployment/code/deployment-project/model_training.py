# ============================================================
# Section: Training a model
# This code is meant to run in a Jupyter notebook (model-training.ipynb).
# It trains a RandomForest pipeline and serializes it to model.bin.
# ============================================================

import numpy as np
import sklearn
import pickle

# Loading the data
available_data = np.genfromtxt("train.csv", delimiter=";", skip_header=1)

# Separating the target from inputs:
y = available_data[:, 11]
X = available_data[:, 0:11]

# Splitting the data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# We want to wrap everything into single composite estimator of sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer

model_pipeline = make_pipeline(MinMaxScaler(), SimpleImputer(), RandomForestRegressor(random_state=42))

# Performing cross-validation
from sklearn.model_selection import cross_val_score
cross_val_score(model_pipeline, X_train, y_train, cv=3)

# Final training on the entire training data
model_pipeline.fit(X_train, y_train)

# Serializing the model
with open("model.bin", "wb") as f_out:
    pickle.dump(model_pipeline, f_out)

print("Model serialized to model.bin")
