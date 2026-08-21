# ============================================================
# Section: Flask - ML prediction web app
# Run with: python 02_flask_predict.py
# Test with: python 03_test_flask.py (in another terminal)
# ============================================================

import pickle
from flask import Flask, request, jsonify

# Load the trained model
with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)

# Create the Flask app
app = Flask("iris_app")

@app.route("/predict", methods=["POST"])
def predict_endpoint():
    data_to_predict = request.get_json()
    y_pred = trained_model.predict(data_to_predict)
    return jsonify({"prediction": y_pred.tolist()})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
