# ============================================================
# Section: Test 2 - Checking that our web app works
# Make sure predict.py is running in another terminal.
# This code is meant to run in a Jupyter notebook (predict-locally.ipynb)
# or as a standalone script.
# ============================================================

import numpy as np
import time
import requests

prod_data = np.genfromtxt("prod-inputs.csv", delimiter=",", skip_header=1)
one_wine = prod_data[0, :]

start_time = time.time()
url = "http://127.0.0.1:9696/predict"
response = requests.post(url, json=prod_data.tolist())
print("--- %s seconds ---" % (time.time() - start_time))
print("Response:", response.text)
