# MLflow - Managing the Machine Learning Lifecycle

This guide covers MLflow basics: tracking experiments, logging models, and managing the ML lifecycle.

---

## 1. Introduction

MLflow is an open-source platform developed by Databricks (2018) to manage the end-to-end machine learning lifecycle. It addresses the complexity of ML development where you need to track not just code, but also datasets, parameters, and model versions.

MLflow provides:
- Reproducibility of experiments
- Standardized model packaging
- Collaboration through shared tracking
- Scalability from local to enterprise workflows

---

## 2. Key Components

### 2.1 MLflow Tracking

API and UI for logging parameters, metrics, and artifacts during ML runs.

- **Experiments** — groups of related runs
- **Runs** — single executions of training code
- **Parameters** — hyperparameters and config values
- **Metrics** — accuracy, loss, etc.
- **Artifacts** — files like models, plots, data

Data is stored locally in `mlruns/` directory by default, or on a remote server.

### 2.2 MLflow Projects

Standard format for packaging ML code with dependencies.

- Contains an `MLproject` YAML file specifying name, dependencies, and entry points
- Ensures anyone can reproduce experiments with consistent results
- MLflow can auto-setup environments (conda, Docker) via `mlflow run`
- Records Git commit hash alongside runs for code versioning

### 2.3 MLflow Models

Standardized format for packaging models for deployment.

When you save a model, MLflow creates:
- Model data (pickle, torch script, etc.)
- `MLmodel` metadata file
- Environment files (conda.yaml, requirements.txt)

Models support multiple **flavors** (e.g., sklearn model can be loaded as sklearn or generic Python function).

Deploy options: local REST API, AWS SageMaker, Azure ML, Spark UDF.

### 2.4 MLflow Model Registry

Centralized store for managing model lifecycle.

- Register models with human-friendly names
- Version models (v1, v2, v3...)
- Assign stages: `Staging`, `Production`, `Archived`
- Track lineage and transitions
- Annotate with descriptions and tags

---

## 3. MLflow and Git Integration

When running experiments from a Git-tracked project, MLflow automatically logs the Git commit hash. This allows you to trace any model back to the exact code version:

```bash
git checkout a1b2c3d
```

---

## 4. Installation and Setup

### 4.1 Install MLflow

Create environment and install:

```bash
conda create -n mlflow_env python=3.12
conda activate mlflow_env
pip install mlflow
```

Verify installation:

```bash
mlflow --version
```

Install additional frameworks as needed:

```bash
pip install scikit-learn
```

### 4.2 Running the Tracking UI

Launch the MLflow web interface:

```bash
mlflow ui
```

Navigate to http://127.0.0.1:5000 in your browser.

If that doesn't work, try:

```bash
mlflow ui --host 127.0.0.1 --port 5000
```

The UI shows all experiments and runs with parameters, metrics, and artifacts.

### 4.3 (Optional) Set Up a Tracking Server

By default, MLflow stores data locally in `mlruns/`. For team collaboration, set up a central server:

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./artifacts \
  --host 0.0.0.0 \
  --port 5000
```

Point your code to a remote server:

```bash
# Via environment variable
export MLFLOW_TRACKING_URI=http://your-remote-server:5000
```

Or in Python:

```python
mlflow.set_tracking_uri("http://your-remote-server:5000")
```

---

## 5. Practical Example

### 5.1 Training and Logging a Model

Create a notebook or script:

```python
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
```

Load and split data:

```python
# Load dataset
iris = load_iris()
X = iris.data
y = iris.target

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

Train model and log to MLflow:

```python
# Start an MLflow run
with mlflow.start_run() as run:

    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # Log hyperparameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 5)

    # Evaluate and log metrics
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    mlflow.log_metric("accuracy", acc)

    # Log artifact (feature importances)
    np.savetxt("feature_importances.txt", model.feature_importances_)
    mlflow.log_artifact("feature_importances.txt")

    # Define signature and input example
    signature = infer_signature(X_train, model.predict(X_train))
    input_example = X_train[:3]

    # Log the model
    mlflow.sklearn.log_model(
        sk_model=model,
        name="my_model",
        signature=signature,
        input_example=input_example
    )

    # Set a tag
    mlflow.set_tag("model_type", "RandomForestClassifier")

    # Print run ID
    run_id = run.info.run_id
    print(f"Finished MLflow run with run_id: {run_id}")
```

Open the MLflow UI to see your logged run with parameters, metrics, and artifacts.

### 5.2 Loading a Saved Model

Load model using the run ID:

```python
run_id = "your_run_id_here"
loaded_model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

# Use the loaded model
loaded_predictions = loaded_model.predict(X_test)
print("Sample predictions:", loaded_predictions[:5])
print("Actual labels:", y_test[:5])
```

### 5.3 (Optional) Registering a Model

Register model to the Model Registry:

```python
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri=model_uri, name="IrisRandomForest")
```

This creates version 1 of "IrisRandomForest" in the registry. You can then transition it to `Staging` or `Production` via the UI or API.

---

## 6. Searching and Comparing Runs

Find runs that meet criteria:

```python
mlflow.search_runs()
```

Use the UI to visually compare metrics across runs.

---

## 7. Best Practices

### Log Everything for Reproducibility

- Parameters and hyperparameters
- Metrics (training and validation)
- Artifacts (models, plots, data samples)
- Random seeds
- Data versions or sample IDs
- Git commit hash (logged automatically)

### Organize Experiments

- Use meaningful experiment names (e.g., "Iris_RF_Tuning")
- Use tags and naming conventions for runs
- Group related runs in the same experiment

### Use Autologging

MLflow can automatically log parameters and metrics for popular frameworks:

```python
mlflow.sklearn.autolog()
# Then train your model as usual
```

Supported: scikit-learn, TensorFlow, PyTorch, XGBoost, and more.

### Centralize for Team Collaboration

- Set up a central tracking server
- All team members point to the same server
- Everyone can view and compare results

### Use Model Registry for Production

- Register best models with clear names
- Use stages: `None` → `Staging` → `Production`
- Version models for easy rollback
- Connect CI/CD pipelines to the registry

### Track Environment and Dependencies

- MLflow saves conda/requirements with models
- Consider logging `pip freeze` output as artifact
- Note key library versions as parameters

### Keep Experiments Clean

- Use descriptive experiment names with dates/versions
- Archive old experiments
- Delete unnecessary intermediate runs
- Archive deprecated models in registry

---

## Quick Reference

### CLI Commands

| Command | Purpose |
|---------|---------|
| `mlflow --version` | Check MLflow version |
| `mlflow ui` | Launch tracking UI |
| `mlflow ui --port 5000` | Launch UI on specific port |
| `mlflow server --backend-store-uri sqlite:///mlflow.db` | Start tracking server |
| `mlflow run .` | Run MLflow project |

### Python API - Tracking

| Function | Purpose |
|----------|---------|
| `mlflow.start_run()` | Start a new run |
| `mlflow.log_param("name", value)` | Log a parameter |
| `mlflow.log_metric("name", value)` | Log a metric |
| `mlflow.log_artifact("file.txt")` | Log a file |
| `mlflow.set_tag("key", "value")` | Set a tag |
| `mlflow.set_experiment("name")` | Set active experiment |
| `mlflow.search_runs()` | Search runs |

### Python API - Models

| Function | Purpose |
|----------|---------|
| `mlflow.sklearn.log_model(model, "name")` | Log sklearn model |
| `mlflow.sklearn.load_model("runs:/{id}/model")` | Load sklearn model |
| `mlflow.register_model(uri, "name")` | Register model |
| `infer_signature(X, y)` | Infer model signature |

### Model URI Formats

| Format | Example |
|--------|---------|
| Run artifact | `runs:/<run_id>/model` |
| Registered model | `models:/<model_name>/<version>` |
| Registered model stage | `models:/<model_name>/Production` |
