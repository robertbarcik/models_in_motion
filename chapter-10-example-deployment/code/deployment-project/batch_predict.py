# ============================================================
# Section: The other shape - batch scoring
# Scores a whole CSV of wines at once and writes a predictions CSV.
# Run with: python batch_predict.py incoming.csv predictions.csv
# ============================================================

import sys
import pickle
import numpy as np

input_path, output_path = sys.argv[1], sys.argv[2]

with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)

X = np.genfromtxt(input_path, delimiter=",", skip_header=1)
y_pred = trained_model.predict(X)

np.savetxt(output_path, y_pred, fmt="%.2f", header="quality",
           comments="")
print(f"scored {len(y_pred)} wines -> {output_path}")
