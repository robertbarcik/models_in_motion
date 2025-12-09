# Testing Traditional Machine Learning Systems (Pre-Deployment)

Welcome to the Testing module! This README contains all the code examples from the tutorial, organized step-by-step so you can follow along.

## 1. Introduction

Testing machine learning systems before deployment is crucial for catching issues in data, code, and model behavior early. Unlike traditional software, ML systems involve data pipelines and models that introduce new types of potential errors. A full ML pipeline needs tests beyond just code correctness – it requires validating input data, checking feature engineering, assessing new model versions' quality, verifying serving infrastructure, and ensuring all pipeline components work together.

---

## Environment Setup

First, create a new environment, activate it, and install necessary libraries:

```bash
conda create -n ml_test_demo python=3.10
conda activate ml_test_demo
pip install pandas numpy scipy pandera pytest jupyter scikit-learn matplotlib seaborn
```

Open Jupyter notebook:

```bash
jupyter notebook
```

---

## Creating Toy Datasets

Copy-paste the below code to create toy datasets `train_df` and `new_df` in Jupyter notebook:

```python
import numpy as np
import pandas as pd

def make_datasets_with_errors(random_state=42):
    np.random.seed(random_state)

    train_df = pd.DataFrame({
        "age": np.random.randint(0, 121, 100),
        "city": np.random.choice(["London", "Paris", "New York"], 100, p=[0.3, 0.3, 0.4]),
        "featureX": np.random.normal(0, 1, 100),
        "user_id": np.arange(1, 101)
    })

    new_df = pd.DataFrame({
        "age": np.random.randint(-100, 121, 50),
        "city": np.random.choice(["London", "Paris", "New York"], 50, p=[0.1, 0.2, 0.7]),
        "featureX": np.random.normal(0.5, 1.2, 50),
        "user_id": np.arange(1001, 1051)
    })

    return train_df, new_df
```

Print created dataframe:

```python
train_df, new_df = make_datasets_with_errors()
train_df.head()
```

---

## 2. Data Quality and Schema Validation with Pandera

Pandera is a Python library that provides a flexible toolkit for validating pandas DataFrames against a predefined schema.

### Defining and Validating Schema

```python
import pandera.pandas as pa
from pandera import Column, Check, DataFrameSchema
from pandera.errors import SchemaError

# Defining Schema
schema = DataFrameSchema({
    "age": Column(int, [
        Check.greater_than_or_equal_to(0),
        Check.less_than_or_equal_to(120)
    ]),
    "city": Column(str, Check.isin(["London", "Paris", "New York"]))
})

# Validate with try/except block for clean error handling
try:
    schema.validate(new_df)
    print("✅ Schema validation passed.")
except SchemaError as e:
    print("❌ Schema validation failed.")
    print(e.failure_cases)
```

In this snippet, we define a schema with two columns:
- **age column**: must be of type `int` and satisfy 2 checks: value must be >= 0 and <= 120
- **city column**: must be a string and must be 1 of the allowed values in the list

---

## 3. Distribution Mismatch Tests (Kolmogorov–Smirnov & Chi-square)

### 3.1 Kolmogorov–Smirnov (K-S) Test (Two-Sample)

The K-S test checks if two samples come from the same distribution.

```python
from scipy.stats import ks_2samp

# Compare distribution of feature "age" in training vs new data
statistic, p_value = ks_2samp(train_df["age"], new_df["age"])
print(f"KS test p-value for 'age': {p_value:.3f}")

if p_value < 0.05:
    print("Warning: 'age' distribution in new data differs from training data.")
```

### Visualizing Distribution Differences

Create a histogram comparing the distribution:

```python
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.histplot(train_df["age"], color="blue", label="train_df", stat="density", bins=20)
sns.histplot(new_df["age"], color="red", label="new_df", stat="density", bins=20)
plt.title("Age Distribution: train_df vs new_df")
plt.xlabel("Age")
plt.ylabel("Density")
plt.legend()
plt.show()
```

### 3.2 Chi-square Test

For categorical data, the Chi-square test is used to detect distribution mismatches:

```python
import numpy as np
from scipy.stats import chisquare

# Category counts in training and new data for feature "city"
train_counts = train_df["city"].value_counts()
new_counts = new_df["city"].value_counts()

# Align the two distributions by category
categories = train_counts.index.union(new_counts.index)
train_freq = np.array([train_counts.get(cat, 0) for cat in categories])
new_freq = np.array([new_counts.get(cat, 0) for cat in categories])

# Chi-square goodness-of-fit: expected frequencies scaled from train distribution
expected = train_freq * (new_freq.sum() / train_freq.sum())
chi_stat, p_value = chisquare(f_obs=new_freq, f_exp=expected)

print(f"Chi-square test p-value for 'city': {p_value:.3f}")
```

### Comparing Category Distributions

```python
# Get percentages
train_dist = train_df["city"].value_counts(normalize=True).mul(100).round(1)
new_dist = new_df["city"].value_counts(normalize=True).mul(100).round(1)

# Combine into a single DataFrame
comparison_df = pd.DataFrame({
    "Train (%)": train_dist,
    "New (%)": new_dist
}).fillna(0).astype(float)

# Sort by Train (%)
comparison_df = comparison_df.sort_values("Train (%)", ascending=False)

# Print
print("City distribution comparison (%):")
display(comparison_df)
```

---

## 4. Unit Testing ML Functions with Pytest

### Create ml_utils.py Script

Create a file called `ml_utils.py`:

```python
# ml_utils.py script:
from sklearn.metrics import recall_score

def compute_recall(y_true, y_pred):
    """
    Compute recall for binary classification using scikit-learn.

    Parameters:
        y_true (list or array): Ground truth labels (0/1)
        y_pred (list or array): Predicted labels (0/1)

    Returns:
        float: Recall score (between 0 and 1)
    """
    return recall_score(y_true, y_pred, zero_division=0)
```

### Create Tests Folder and Test File

```bash
mkdir tests
cd tests
```

Create a unit test in `test_ml_utils.py`:

```python
# test_ml_utils.py:
from ml_utils import compute_recall

def test_compute_recall_basic():
    y_true = [1, 0, 1, 1]
    y_pred = [1, 0, 0, 1]
    expected_recall = 2 / 3
    assert compute_recall(y_true, y_pred) == expected_recall
```

### Run the Tests

Go back to the project root:

```bash
cd ..
```

Make sure pytest is installed:

```bash
pip install pytest
```

Run the tests:

```bash
PYTHONPATH=. pytest -q
```

You should see: `1 passed in 14.74s`

---

## 5. Integration Testing the Full Pipeline

Integration tests ensure all components work together. Here's an example:

```python
# In test_pipeline.py
import pandas as pd
from my_pipeline import load_model, preprocess_data, predict  # pipeline functions

def test_full_pipeline(tmp_path):
    # 1. Arrange: create a small sample input dataset
    sample_data = pd.DataFrame({
        "age": [25, 40, 90],
        "city": ["London", "Paris", "New York"],
        "featureX": [0.5, 1.2, 3.3]
    })
    sample_data_path = tmp_path / "sample.csv"
    sample_data.to_csv(sample_data_path, index=False)

    # 2. Act: run the pipeline end-to-end (simulate what production would do)
    model = load_model("model.joblib")
    data = preprocess_data(pd.read_csv(sample_data_path))
    preds = predict(model, data)  # get model predictions

    # 3. Assert: validate the output
    assert preds.shape[0] == sample_data.shape[0]  # got prediction for each input
    # predictions are in expected range [0,1]
    assert all(0.0 <= p <= 1.0 for p in preds)
```

---

## 6. Invariance Testing for Model Robustness

Invariance tests check model robustness under small input perturbations.

### 6.1 Dataset Generation

Create a synthetic dataset with informative, irrelevant, and redundant features:

```python
import numpy as np
import pandas as pd

def generate_customer_data(num_samples=2000):
    """
    Args:
        num_samples (int): The number of customer samples to generate.

    Returns:
        pandas.DataFrame: A DataFrame containing the synthetic customer data.
    """
    print(f"Generating a synthetic dataset with {num_samples} samples...\n")
    np.random.seed(42)  # for reproducibility

    # -- Informative Features --
    # 'age': Older customers are slightly more likely to purchase.
    age = np.random.randint(18, 70, size=num_samples)

    # 'monthly_income': Higher income strongly increases purchase probability.
    monthly_income = np.random.randint(2000, 15000, size=num_samples)

    # 'subscription_plan': 'Premium' members are most likely to purchase.
    plans = ['None', 'Basic', 'Premium']
    subscription_plan = np.random.choice(plans, size=num_samples, p=[0.5, 0.3, 0.2])

    # -- Irrelevant Features --
    # 'user_id': A unique identifier for each customer.
    user_id = np.arange(10000, 10000 + num_samples)

    # 'random_noise_feature': A column of pure random numbers.
    random_noise_feature = np.random.randn(num_samples)

    # -- Redundant Feature --
    # 'credit_score': Higher income often correlates with a better credit score.
    credit_score = (monthly_income / 20) + np.random.normal(0, 25, size=num_samples)
    credit_score = np.clip(credit_score, 300, 850).astype(int)

    # -- Target Variable: 'will_purchase' --
    purchase_probability = 1 / (1 + np.exp(-(
        -12 +
        (age / 10) +
        (monthly_income / 2000) +
        (subscription_plan == 'Basic') * 1 +
        (subscription_plan == 'Premium') * 3
    )))

    will_purchase = (purchase_probability > np.random.rand(num_samples)).astype(int)

    # Assemble the DataFrame
    df = pd.DataFrame({
        'user_id': user_id,
        'age': age,
        'monthly_income': monthly_income,
        'credit_score': credit_score,
        'subscription_plan': subscription_plan,
        'random_noise_feature': random_noise_feature,
        'will_purchase': will_purchase
    })

    print("Dataset created with the following columns:")
    print(df.info())
    print("\nTarget variable distribution:")
    print(df['will_purchase'].value_counts(normalize=True))
    print("-" * 50)

    return df
```

Create the dataset:

```python
customer_df = generate_customer_data()
customer_df
```

### 6.2 Model Training

Train a Random Forest classifier:

```python
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_model(df):
    """
    Preprocesses the data, splits it, and trains a RandomForestClassifier.

    Args:
        df (pandas.DataFrame): The input DataFrame with features and target.

    Returns:
        tuple: A tuple containing the trained model, the processed test set (X_test),
               the test labels (y_test), the feature names, and the encoder.
    """
    print("Starting model training process...")

    # Define features (X) and target (y)
    X = df.drop('will_purchase', axis=1)
    y = df['will_purchase']

    # Identify categorical and numerical features
    categorical_features = ['subscription_plan']
    numerical_features = ['age', 'monthly_income', 'credit_score', 'random_noise_feature']

    # Note: 'user_id' is an identifier and should be dropped before training.
    X = X.drop('user_id', axis=1)

    print(f"\nIdentified Features for Training:")
    print(f"  Numerical: {numerical_features}")
    print(f"  Categorical: {categorical_features}")

    # Preprocessing: One-Hot Encode categorical features
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_cats = encoder.fit_transform(X[categorical_features])
    encoded_cat_names = encoder.get_feature_names_out(categorical_features)

    # Create a DataFrame with the encoded columns
    X_encoded_cats = pd.DataFrame(encoded_cats, columns=encoded_cat_names, index=X.index)

    # Combine numerical and encoded categorical features
    X_processed = pd.concat([X[numerical_features], X_encoded_cats], axis=1)

    # Store final feature names
    feature_names = X_processed.columns.tolist()
    print(f"\nFinal features after one-hot encoding: {feature_names}")

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"\nData split into {len(X_train)} training samples and {len(X_test)} testing samples.")

    # Train a RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, min_samples_leaf=5)
    model.fit(X_train, y_train)

    # Evaluate baseline performance
    base_predictions = model.predict(X_test)
    base_accuracy = accuracy_score(y_test, base_predictions)

    print(f"\nModel training complete.")
    print(f"Baseline Accuracy on the test set: {base_accuracy:.4f}")
    print("-" * 50)

    return model, X_test, y_test, feature_names, encoder
```

Train the model:

```python
model, X_test, y_test, feature_names, encoder = train_model(customer_df)
```

### 6.3 Invariance Tests

#### 6.3.1 Testing Noise Invariance

Test if model predictions are stable with small random noise:

```python
def test_noise_invariance(model, X_test, num_samples=5):
    print(">>> Test 1: Noise Invariance Test <<<")
    print("We add a tiny amount of random noise to numerical inputs.")
    print("A robust model's predictions should NOT change.\n")

    # Try increasing the noise_level to see when predictions start to flip.
    noise_level = 0.01  # 1% noise

    # Take a small sample from the test set
    sample_data = X_test.head(num_samples).copy()
    original_predictions = model.predict(sample_data)

    # Add noise to numerical features only
    noisy_data = sample_data.copy()
    numerical_cols = ['age', 'monthly_income', 'credit_score']

    for col in numerical_cols:
        noise = np.random.normal(0, noisy_data[col].std() * noise_level, size=noisy_data[col].shape)
        noisy_data[col] += noise

    # Get predictions on the noisy data
    noisy_predictions = model.predict(noisy_data)

    print(f"Comparing predictions for the first {num_samples} samples:")
    results = pd.DataFrame({
        'Original Prediction': original_predictions,
        'Noisy Prediction': noisy_predictions
    })
    results['Prediction Flipped?'] = results['Original Prediction'] != results['Noisy Prediction']
    print(results)

    num_flipped = results['Prediction Flipped?'].sum()
    print(f"\nResult: Out of {num_samples} samples, {num_flipped} predictions flipped after adding {noise_level*100}% noise.")

    if num_flipped == 0:
        print("✅ PASSED: The model is robust to small amounts of noise.")
    else:
        print("⚠️ CAUTION: The model's predictions are sensitive to minor input noise.")
    print("-" * 50)
```

Run the test:

```python
test_noise_invariance(model, X_test)
```

#### 6.3.2 Irrelevant Feature Shuffling

Test the model's reliance on irrelevant features:

```python
def test_irrelevant_feature_shuffling(model, X_test, y_test, feature_to_shuffle):
    print(f">>> Test 2: Irrelevant Feature Shuffling (Testing '{feature_to_shuffle}') <<<")
    print(f"We shuffle the '{feature_to_shuffle}' column to break its link to the target.")
    print("If the model has correctly learned this feature is useless, accuracy should not change.\n")

    # 1. Get baseline accuracy
    base_predictions = model.predict(X_test)
    base_accuracy = accuracy_score(y_test, base_predictions)

    # 2. Shuffle the selected feature column
    X_test_shuffled = X_test.copy()
    # Shuffle the column values. .values is important to avoid index alignment issues.
    shuffled_values = X_test_shuffled[feature_to_shuffle].sample(frac=1, random_state=42).values
    X_test_shuffled[feature_to_shuffle] = shuffled_values

    # 3. Get new accuracy
    shuffled_predictions = model.predict(X_test_shuffled)
    shuffled_accuracy = accuracy_score(y_test, shuffled_predictions)

    # 4. Compare and report
    accuracy_drop = base_accuracy - shuffled_accuracy

    print(f"  - Baseline Accuracy: {base_accuracy:.4f}")
    print(f"  - Accuracy after shuffling '{feature_to_shuffle}': {shuffled_accuracy:.4f}")
    print(f"  - Accuracy Drop: {accuracy_drop:.4f}")

    if accuracy_drop < 0.02:
        print(f"✅ PASSED: The model correctly ignored the irrelevant '{feature_to_shuffle}' feature.")
    else:
        print(f"⚠️ CAUTION: The model seems to be relying on the '{feature_to_shuffle}' feature, which it shouldn't.")
        print("  This might indicate overfitting or a pattern in the 'random' data.")
    print("-" * 50)
```

Run the test:

```python
test_irrelevant_feature_shuffling(
    model, X_test, y_test,
    feature_to_shuffle='random_noise_feature'
)
```

#### 6.3.3 Informative Feature Shuffling

Test that shuffling an informative feature hurts performance:

```python
def test_informative_feature_shuffling(model, X_test, y_test, feature_to_shuffle):
    print(f">>> Contrast Test: Shuffling an INFORMATIVE feature ('{feature_to_shuffle}') <<<")
    print("Now, we shuffle an important feature. We expect accuracy to drop significantly.\n")

    base_predictions = model.predict(X_test)
    base_accuracy = accuracy_score(y_test, base_predictions)

    X_test_shuffled = X_test.copy()
    shuffled_values = X_test_shuffled[feature_to_shuffle].sample(frac=1, random_state=42).values
    X_test_shuffled[feature_to_shuffle] = shuffled_values

    shuffled_predictions = model.predict(X_test_shuffled)
    shuffled_accuracy = accuracy_score(y_test, shuffled_predictions)

    accuracy_drop = base_accuracy - shuffled_accuracy

    print(f"  - Baseline Accuracy: {base_accuracy:.4f}")
    print(f"  - Accuracy after shuffling '{feature_to_shuffle}': {shuffled_accuracy:.4f}")
    print(f"  - Accuracy Drop: {accuracy_drop:.4f}")

    if accuracy_drop > 0.1:
        print(f"✅ PASSED: As expected, model performance dropped significantly.")
        print("  This confirms the model was correctly using this informative feature.")
    else:
        print(f"⚠️ CAUTION: Model performance did not drop much.")
        print("  This might mean the model isn't using this feature effectively or other features are redundant.")
    print("-" * 50)
```

Run the test:

```python
test_informative_feature_shuffling(
    model, X_test, y_test,
    feature_to_shuffle='monthly_income'
)
```

---

## 7. Additional Validation Tests

### 7.1 Dataset and Model Setup

Create a synthetic dataset for customer churn prediction:

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

def generate_churn_data(num_samples=1000, random_state=42):
    """
    Generate synthetic customer churn dataset.
    """
    np.random.seed(random_state)

    # Numerical features
    age = np.random.randint(18, 70, size=num_samples)
    monthly_charges = np.random.uniform(20, 100, size=num_samples)
    tenure_months = np.random.randint(1, 72, size=num_samples)

    # Categorical features
    contract_type = np.random.choice(
        ['Month-to-month', 'One year', 'Two year'],
        size=num_samples,
        p=[0.5, 0.3, 0.2],
    )
    payment_method = np.random.choice(
        ['Credit card', 'Bank transfer', 'Electronic check'],
        size=num_samples,
        p=[0.4, 0.35, 0.25],
    )

    # Target: churn probability based on features
    churn_probability = 1 / (1 + np.exp(-(
        -2 +
        (monthly_charges / 50) -
        (tenure_months / 24) +
        (contract_type == 'Month-to-month') * 1.5 +
        (payment_method == 'Electronic check') * 0.8
    )))

    churn = (churn_probability > np.random.rand(num_samples)).astype(int)

    df = pd.DataFrame({
        'age': age,
        'monthly_charges': monthly_charges,
        'tenure_months': tenure_months,
        'contract_type': contract_type,
        'payment_method': payment_method,
        'churn': churn
    })

    print(f"Dataset created with {num_samples} samples.")
    print(f"Churn rate: {churn.mean():.2%}")

    return df
```

Generate the dataset:

```python
churn_df = generate_churn_data()
churn_df.head()
```

Build a preprocessing pipeline with Logistic Regression:

```python
def build_and_train_pipeline(df):
    """
    Build a preprocessing pipeline with Logistic Regression.
    """
    # Separate features and target
    X = df.drop("churn", axis=1)
    y = df["churn"]

    # Define feature types
    numerical_features = ["age", "monthly_charges", "tenure_months"]
    categorical_features = ["contract_type", "payment_method"]

    # Create preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    # Create full pipeline
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(random_state=42, max_iter=1000)),
        ]
    )

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Train the pipeline
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("Pipeline trained successfully.")
    print(f"Test Accuracy: {accuracy:.4f}")

    return pipeline, X_test, y_test
```

Train the pipeline:

```python
pipeline, X_test, y_test = build_and_train_pipeline(churn_df)
```

### 7.2 Missing Value Handling Tests

```python
import numpy as np
import pandas as pd

def test_missing_value_handling(model, X_test, feature_names=None):
    """
    Test how the model/pipeline handles missing values in input data.
    """
    print(">>> Test: Missing Value Handling <<<")
    print(
        "We introduce NaN values into the input to verify the pipeline handles "
        "them.\n"
    )

    # Create a copy with some missing values
    X_with_missing = X_test.head(10).copy()

    # Introduce NaN in different numerical columns
    X_with_missing.iloc[0, 0] = np.nan  # First row, first column
    X_with_missing.iloc[2, 1] = np.nan  # Third row, second column
    X_with_missing.iloc[5, 0] = np.nan  # Sixth row, first column

    print(f"Introduced {X_with_missing.isna().sum().sum()} missing values in test samples.")

    try:
        predictions = model.predict(X_with_missing)
        print("✅ PASSED: Pipeline handled missing values successfully.")
        print(f"  Generated {len(predictions)} predictions.")

        # Check if predictions are valid (not NaN)
        if np.any(np.isnan(predictions)):
            print("⚠️ WARNING: Some predictions are NaN - check imputation logic.")
        else:
            print("  All predictions are valid (non-NaN).")
    except Exception as e:
        print("❌ FAILED: Pipeline crashed with missing values.")
        print(f"  Error: {type(e).__name__}: {e}")
        print("  Consider adding imputation or input validation to your pipeline.")
    print("-" * 50)
```

Run the test:

```python
test_missing_value_handling(pipeline, X_test)
```

### 7.3 Performance/Latency Tests

```python
import time

def test_inference_latency(pipeline, X_test, max_latency_ms=100, num_iterations=100):
    """
    Test that model inference meets latency requirements.

    Args:
        pipeline: Trained pipeline
        X_test: Test dataset
        max_latency_ms: Maximum acceptable latency in milliseconds
        num_iterations: Number of predictions to average over
    """
    print(">>> Test: Inference Latency <<<")
    print(f"Testing if single-sample inference completes within {max_latency_ms}ms.\n")

    # Test single-sample prediction latency
    single_sample = X_test.head(1)
    latencies = []

    for _ in range(num_iterations):
        start_time = time.time()
        _ = pipeline.predict(single_sample)
        latency_ms = (time.time() - start_time) * 1000
        latencies.append(latency_ms)

    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)

    print(f"Single-sample inference latency ({num_iterations} iterations):")
    print(f"  - Average: {avg_latency:.2f} ms")
    print(f"  - P95: {p95_latency:.2f} ms")
    print(f"  - P99: {p99_latency:.2f} ms")

    # Test batch prediction latency
    batch_sizes = [10, 100, 250]
    print("\nBatch inference latency:")

    for batch_size in batch_sizes:
        if batch_size <= len(X_test):
            batch_sample = X_test.head(batch_size)
            start_time = time.time()
            _ = pipeline.predict(batch_sample)
            batch_latency = (time.time() - start_time) * 1000
            per_sample = batch_latency / batch_size
            print(
                f"  - Batch size {batch_size}: {batch_latency:.2f} ms total "
                f"({per_sample:.3f} ms/sample)"
            )

    # Pass/Fail evaluation
    if p95_latency <= max_latency_ms:
        print(
            f"\n✅ PASSED: P95 latency ({p95_latency:.2f}ms) is within "
            f"{max_latency_ms}ms requirement."
        )
    else:
        print(
            f"\n❌ FAILED: P95 latency ({p95_latency:.2f}ms) exceeds "
            f"{max_latency_ms}ms requirement."
        )
        print("  Consider: simpler model, fewer features, or model optimization.")
    print("-" * 50)
```

Run the test:

```python
test_inference_latency(pipeline, X_test, max_latency_ms=100)
```

### 7.4 Model Regression Tests

```python
from sklearn.metrics import accuracy_score, f1_score

def test_model_regression(
    pipeline,
    X_test,
    y_test,
    baseline_accuracy=None,
    min_accuracy=0.70,
    tolerance=0.02,
):
    """
    Test that the current model meets minimum performance requirements
    and doesn't regress compared to a baseline.

    Args:
        pipeline: The pipeline being tested
        X_test: Test features (golden dataset)
        y_test: True labels (golden dataset)
        baseline_accuracy: Previous model's accuracy (if available)
        min_accuracy: Minimum acceptable accuracy
        tolerance: Acceptable drop from baseline
    """
    print(">>> Test: Model Regression Test <<<")
    print("Verifying model performance meets requirements and hasn't regressed.\n")

    # Get current model predictions and metrics
    predictions = pipeline.predict(X_test)
    current_accuracy = accuracy_score(y_test, predictions)
    current_f1 = f1_score(y_test, predictions, average="weighted")

    print("Current Model Performance:")
    print(f"  - Accuracy: {current_accuracy:.4f}")
    print(f"  - F1 Score: {current_f1:.4f}")

    all_passed = True

    # Check 1: Minimum accuracy threshold
    print(f"\n[Check 1] Minimum Accuracy Threshold: {min_accuracy}")
    if current_accuracy >= min_accuracy:
        print(f"  ✅ PASSED: Accuracy {current_accuracy:.4f} >= {min_accuracy}")
    else:
        print(f"  ❌ FAILED: Accuracy {current_accuracy:.4f} < {min_accuracy}")
        all_passed = False

    # Check 2: Regression from baseline (if baseline provided)
    if baseline_accuracy is not None:
        print(
            f"\n[Check 2] Regression from Baseline: {baseline_accuracy:.4f} "
            f"(tolerance: {tolerance})"
        )
        accuracy_drop = baseline_accuracy - current_accuracy

        if accuracy_drop <= tolerance:
            print(f"  ✅ PASSED: Accuracy drop ({accuracy_drop:.4f}) within tolerance")
        else:
            print(
                f"  ❌ FAILED: Accuracy drop ({accuracy_drop:.4f}) exceeds tolerance "
                f"({tolerance})"
            )
            all_passed = False
    else:
        print("\n[Check 2] Baseline comparison: SKIPPED (no baseline provided)")
        print(
            f"  TIP: Save current accuracy ({current_accuracy:.4f}) as baseline for "
            "future tests."
        )

    # Check 3: Sanity check - better than random
    random_baseline = max(y_test.mean(), 1 - y_test.mean())
    print(f"\n[Check 3] Better than Random Baseline: {random_baseline:.4f}")

    if current_accuracy > random_baseline:
        print(
            f"  ✅ PASSED: Model ({current_accuracy:.4f}) beats random "
            f"({random_baseline:.4f})"
        )
    else:
        print(
            f"  ❌ FAILED: Model ({current_accuracy:.4f}) doesn't beat random "
            f"({random_baseline:.4f})"
        )
        all_passed = False

    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL REGRESSION TESTS PASSED")
    else:
        print("❌ SOME REGRESSION TESTS FAILED - Review before deployment")
    print("-" * 50)

    return current_accuracy
```

Run the test:

```python
current_accuracy = test_model_regression(
    pipeline, X_test, y_test,
    baseline_accuracy=None,
    min_accuracy=0.70
)
```

---

## 8. Conclusion

Testing traditional ML systems before deployment is essential for reliable production machine learning. By combining:

- **Data validation** (schemas and checks on input data)
- **Statistical tests** for distribution shifts
- **Unit tests** on feature and metric functions
- **Integration tests** across the entire pipeline
- **Invariance tests** for model robustness

We create a safety net that catches issues early and ensures our model will perform as expected in the real world.

---

## Quick Reference

### Pandera Schema Checks

| Check | Description |
|-------|-------------|
| `Check.greater_than_or_equal_to(0)` | Value >= 0 |
| `Check.less_than_or_equal_to(120)` | Value <= 120 |
| `Check.isin(["A", "B", "C"])` | Value in allowed list |
| `Check.less_than(100)` | Value < 100 |

### Pytest Commands

```bash
# Run all tests
PYTHONPATH=. pytest -q

# Run with verbose output
PYTHONPATH=. pytest -v

# Run specific test file
PYTHONPATH=. pytest tests/test_ml_utils.py

# Run with coverage
PYTHONPATH=. pytest --cov=.
```

### Statistical Test Thresholds

| Test | Threshold | Interpretation |
|------|-----------|----------------|
| K-S Test | p < 0.05 | Distribution has shifted |
| Chi-square | p < 0.05 | Categorical distribution differs |

---

## Best Practices Summary

1. **Validate data at ingestion** - Use schema validation to catch data quality issues early
2. **Monitor for distribution drift** - Use K-S and Chi-square tests to detect training-serving skew
3. **Unit test ML functions** - Test preprocessing, feature engineering, and metric calculations
4. **Integration test the pipeline** - Ensure all components work together end-to-end
5. **Test for invariance** - Verify model robustness to noise and irrelevant features
6. **Set performance baselines** - Track model accuracy and latency requirements
7. **Automate testing** - Run tests in CI/CD before deployment
