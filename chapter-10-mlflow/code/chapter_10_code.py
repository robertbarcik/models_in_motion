# ============================================================
# Chapter 10: MLflow
# All notebook code from this chapter, organized by section.
# Run in a Jupyter notebook or copy sections as needed.
# ============================================================


# ============================================================
# Section: Training and logging an ML model with MLflow
# ============================================================

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# 1. Load dataset (Iris flower data)
iris = load_iris()
X = iris.data
y = iris.target

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Create a named experiment (or use existing one)
mlflow.set_experiment("Iris_Classification")

# 3. Start an MLflow run to track this experiment
with mlflow.start_run() as run:
    # Train a RandomForest model
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # 4. Log hyperparameters (parameters) to MLflow
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 5)

    # 5. Evaluate model on test data and log metrics
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    mlflow.log_metric("accuracy", acc)

    # 6. Log an artifact: save feature importances to a text file
    np.savetxt("feature_importances.txt", model.feature_importances_)
    mlflow.log_artifact("feature_importances.txt")

    # Infer signature and create input example
    signature = infer_signature(X_train, model.predict(X_train))
    input_example = X_train[:3]

    # 7. Log the trained model to MLflow (with the "sklearn" flavor)
    mlflow.sklearn.log_model(sk_model=model,
                             artifact_path="my_model",
                             signature=signature,
                             input_example=input_example)

    # (Optional) set a descriptive tag for the run
    mlflow.set_tag("model_type", "RandomForestClassifier")

    # 8. Print the run ID for reference
    run_id = run.info.run_id
    print(f"Finished MLflow run with run_id: {run_id}")


# ============================================================
# Section: Comparing multiple runs
# ============================================================

configurations = [
    {"n_estimators": 50,  "max_depth": 3},
    {"n_estimators": 100, "max_depth": 5},
    {"n_estimators": 200, "max_depth": 10},
]

for config in configurations:
    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=config["n_estimators"],
            max_depth=config["max_depth"],
            random_state=42
        )
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        acc = accuracy_score(y_test, predictions)

        mlflow.log_param("n_estimators", config["n_estimators"])
        mlflow.log_param("max_depth", config["max_depth"])
        mlflow.log_metric("accuracy", acc)

        print(f"Config {config} → accuracy: {acc:.4f}")


# ============================================================
# Section: A simpler alternative - autologging
# ============================================================

mlflow.sklearn.autolog()

with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)


# ============================================================
# Section: Loading and using a saved model
# ============================================================

# Replace with your actual run_id from the output above
run_id = "here_goes_RUN_ID"
loaded_model = mlflow.sklearn.load_model(f"runs:/{run_id}/my_model")

# Use the loaded model to predict on the test set (or new data)
loaded_predictions = loaded_model.predict(X_test)
print("Sample predictions from loaded model:", loaded_predictions[:5])
print("Actual labels:", y_test[:5])


# ============================================================
# Section: Registering the model in the Model Registry
# ============================================================

# Register the model
model_uri = f"runs:/{run_id}/my_model"
mlflow.register_model(model_uri=model_uri, name="IrisRandomForest")

# Set an alias (e.g., "champion" for the production-ready version)
from mlflow import MlflowClient

client = MlflowClient()
client.set_registered_model_alias(
    name="IrisRandomForest",
    alias="champion",
    version=1
)

# Load model by alias
champion_model = mlflow.sklearn.load_model("models:/IrisRandomForest@champion")


# ============================================================
# Section: Moving to production - track environment
# ============================================================

import sklearn

with mlflow.start_run():
    # Log library versions as parameters
    mlflow.log_param("sklearn_version", sklearn.__version__)
    mlflow.log_param("numpy_version", np.__version__)
    mlflow.log_param("python_version", "3.11")

    # ... hyperparameters, training, metrics ...


# ============================================================
# Section: Moving to production - log everything for reproducibility
# ============================================================

import hashlib

with mlflow.start_run():
    # Reproducibility parameters
    mlflow.log_param("random_seed", 42)
    mlflow.log_param("train_rows", len(X_train))

    # Log a hash of the training data to detect changes
    data_hash = hashlib.md5(X_train.tobytes()).hexdigest()[:8]
    mlflow.log_param("data_hash", data_hash)

    # ... environment params, hyperparameters, training, metrics ...
