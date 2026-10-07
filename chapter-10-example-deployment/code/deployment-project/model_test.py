# ============================================================
# Section: Test 1 - Verifying (de)serialization
# This code is meant to run in a Jupyter notebook (model-use.ipynb).
# It loads the serialized model and generates predictions.
# ============================================================

import pickle
import numpy as np

# Load the serialized model in read-binary mode
with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)

# Load production data
prod_data = np.genfromtxt("prod-inputs.csv", delimiter=",", skip_header=1)

# Generate predictions
predictions = trained_model.predict(prod_data)
print("Predictions:", predictions)
