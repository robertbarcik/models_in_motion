# ============================================================
# Section: Pickle - Serializing a trained model
# ============================================================

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
import pickle

# Load data and train a simple model
X, y = load_iris(return_X_y=True)
model = DecisionTreeClassifier()
model.fit(X, y)

# Serialize the trained model
with open("model.bin", "wb") as f_out:
    pickle.dump(model, f_out)

print("Model serialized to model.bin")


# ============================================================
# Deserialization - loading the model back
# ============================================================

with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)

print("Model loaded successfully")
print("Test prediction:", trained_model.predict([[5.1, 3.5, 1.4, 0.2]]))
