# ============================================================
# Section: Testing the Flask app
# Make sure 02_flask_predict.py is running in another terminal.
# ============================================================

import requests

sample = [[5.1, 3.5, 1.4, 0.2]]
response = requests.post("http://localhost:9696/predict", json=sample)
print(response.json())
