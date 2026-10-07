# ============================================================
# Section: Turning predict.py into a web app
# This is the Flask application that serves predictions.
# Run with: python predict.py
# Test with: python test_predict.py (in another terminal)
# ============================================================

from flask import Flask, request, jsonify
import pickle

with open("model.bin", "rb") as f_in:
    trained_model = pickle.load(f_in)

app = Flask("wines")

@app.route("/predict", methods=["POST"])
def predict():
    wine_to_predict = request.get_json()
    y_pred = trained_model.predict(wine_to_predict)
    return str(y_pred)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
