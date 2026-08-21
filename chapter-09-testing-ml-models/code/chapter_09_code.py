# ============================================================
# Chapter 9: Testing ML Models
# All notebook code from this chapter, organized by section.
# Run in a Jupyter notebook or copy sections as needed.
#
# Separate files in this folder:
#   my_pipeline.py            - ML pipeline module
#   feature_engineering.py    - Feature engineering module
#   test_feature_engineering.py - pytest unit tests
#   test_pipeline.py          - pytest integration tests
# ============================================================


# ============================================================
# Section: Loading datasets
# ============================================================

import pandas as pd

reference_df = pd.read_csv("data/data_reference.csv")
incoming_df = pd.read_csv("data/data_incoming.csv")

print(f"Reference dataset: {reference_df.shape[0]} rows, {reference_df.shape[1]} columns")
print(f"Incoming dataset:  {incoming_df.shape[0]} rows, {incoming_df.shape[1]} columns")
reference_df.head()


# ============================================================
# Section: Data quality and schema validation with Pandera
# ============================================================

import pandera as pa
from pandera import Column, Check, DataFrameSchema
from pandera.errors import SchemaErrors

schema = DataFrameSchema({
    "customer_id": Column(int, nullable=False),
    "age": Column(float, [
        Check.greater_than_or_equal_to(0),
        Check.less_than_or_equal_to(60)
    ], nullable=False),
    "city": Column(str, Check.isin(["London", "Paris", "New York"]), nullable=False),
    "monthly_spend": Column(float, Check.greater_than(0), nullable=False),
    "signup_source": Column(str, Check.isin(["Organic", "Referral", "Paid"]), nullable=False),
})

try:
    schema.validate(incoming_df, lazy=True)
    print("Schema validation passed.")
except SchemaErrors as e:
    print("Schema validation failed.")
    print(e.failure_cases.head(10))


# ============================================================
# Section: Kolmogorov-Smirnov (K-S) test
# ============================================================

from scipy.stats import ks_2samp

statistic, p_value = ks_2samp(
    reference_df["monthly_spend"].dropna(),
    incoming_df["monthly_spend"].dropna()
)

print(f"KS test p-value for 'monthly_spend': {p_value:.3f}")

if p_value < 0.05:
    print("Warning: 'monthly_spend' distribution in incoming data differs from reference data.")


# ============================================================
# Section: K-S test - distribution visualization
# ============================================================

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.histplot(reference_df["monthly_spend"], color="blue", label="reference", stat="density", bins=20)
sns.histplot(incoming_df["monthly_spend"].dropna(), color="red", label="incoming", stat="density", bins=20)
plt.title("monthly_spend Distribution: Reference vs Incoming")
plt.xlabel("monthly_spend")
plt.ylabel("Density")
plt.legend()


# ============================================================
# Section: Chi-square test
# ============================================================

import numpy as np
from scipy.stats import chisquare

train_counts = reference_df["city"].value_counts()
new_counts = incoming_df["city"].value_counts()

categories = train_counts.index.union(new_counts.index)
train_freq = np.array([train_counts.get(cat, 0) for cat in categories])
new_freq = np.array([new_counts.get(cat, 0) for cat in categories])

expected = train_freq * (new_freq.sum() / train_freq.sum())
chi_stat, p_value = chisquare(f_obs=new_freq, f_exp=expected)

print(f"Chi-square test p-value for 'city': {p_value:.3f}")


# ============================================================
# Section: Chi-square - distribution comparison
# ============================================================

train_dist = reference_df["city"].value_counts(normalize=True).mul(100).round(1)
new_dist = incoming_df["city"].value_counts(normalize=True).mul(100).round(1)

comparison_df = pd.DataFrame({
    "Reference (%)": train_dist,
    "Incoming (%)": new_dist
}).fillna(0).astype(float)

comparison_df = comparison_df.sort_values("Reference (%)", ascending=False)

print("City distribution comparison (%):")
print(comparison_df)


# ============================================================
# Section: Model testing setup - load and train model
# ============================================================

train_df = pd.read_csv("data/model_testing_train.csv")
test_df = pd.read_csv("data/model_testing_test.csv")

print(f"Training set: {train_df.shape[0]} rows, {train_df.shape[1]} columns")
print(f"Test set:     {test_df.shape[0]} rows, {test_df.shape[1]} columns")
train_df.head()


# ============================================================
# Section: Noise invariance test
# ============================================================

def test_noise_invariance(model, X_test, num_samples=50):
    print(">>> Test 1: Noise Invariance <<<")
    print("Adding tiny random noise to numerical inputs.")
    print("A robust model's predictions should NOT change.\n")

    noise_level = 0.01  # 1 % noise

    sample = X_test.head(num_samples).copy()
    original_preds = model.predict(sample)

    noisy = sample.copy()
    for col in ["age", "monthly_income", "credit_score"]:
        noise = np.random.normal(0, noisy[col].std() * noise_level, size=len(noisy))
        noisy[col] = noisy[col] + noise

    noisy_preds = model.predict(noisy)

    num_flipped = (original_preds != noisy_preds).sum()
    print(f"Result: {num_flipped} out of {num_samples} predictions flipped "
          f"after adding {noise_level*100}% noise.")

    if num_flipped == 0:
        print("PASSED: The model is robust to small noise.\n")
    else:
        print("CAUTION: Some predictions are sensitive to minor noise.\n")


# ============================================================
# Section: Permutation invariance test
# ============================================================

def test_permutation_invariance(model, X_test, num_samples=50):
    print(">>> Test 2: Permutation Invariance <<<")
    print("Shuffling the order of rows in a batch.")
    print("Each row's prediction should stay the same.\n")

    sample = X_test.head(num_samples).copy()
    original_preds = model.predict(sample)

    shuffled = sample.sample(frac=1, random_state=99)
    shuffled_preds = model.predict(shuffled)

    realigned_preds = pd.Series(shuffled_preds, index=shuffled.index)
    realigned_preds = realigned_preds.loc[sample.index].values

    num_mismatched = (original_preds != realigned_preds).sum()
    print(f"Result: {num_mismatched} out of {num_samples} predictions "
          f"differ after row-order shuffle.")

    if num_mismatched == 0:
        print("PASSED: Predictions are independent of row order.\n")
    else:
        print("FAILED: Row order is affecting predictions — investigate.\n")


# ============================================================
# Section: Irrelevant feature shuffling test
# ============================================================

from sklearn.metrics import accuracy_score

def test_irrelevant_feature_shuffling(model, X_test, y_test,
                                       feature="random_noise",
                                       threshold=0.02):
    print(f">>> Test 3: Irrelevant Feature Shuffling ('{feature}') <<<")
    print(f"Shuffling '{feature}' to break any link to the target.")
    print("If the model correctly ignores this feature, accuracy stays the same.\n")

    base_accuracy = accuracy_score(y_test, model.predict(X_test))

    X_shuffled = X_test.copy()
    X_shuffled[feature] = (
        X_shuffled[feature].sample(frac=1, random_state=42).values
    )
    shuffled_accuracy = accuracy_score(y_test, model.predict(X_shuffled))

    drop = base_accuracy - shuffled_accuracy
    print(f"  Baseline accuracy:             {base_accuracy:.4f}")
    print(f"  Accuracy after shuffling:      {shuffled_accuracy:.4f}")
    print(f"  Accuracy drop:                 {drop:.4f}")

    if drop < threshold:
        print(f"PASSED: The model correctly ignored '{feature}'.\n")
    else:
        print(f"CAUTION: The model seems to rely on '{feature}', "
              f"which it shouldn't.\n")


# ============================================================
# Section: Informative feature shuffling test
# ============================================================

def test_informative_feature_shuffling(model, X_test, y_test,
                                        feature="monthly_income",
                                        threshold=0.05):
    print(f">>> Test 4: Informative Feature Shuffling ('{feature}') <<<")
    print(f"Shuffling '{feature}' to break its link to the target.")
    print("If the model relies on this feature, accuracy should DROP.\n")

    base_accuracy = accuracy_score(y_test, model.predict(X_test))

    X_shuffled = X_test.copy()
    X_shuffled[feature] = (
        X_shuffled[feature].sample(frac=1, random_state=42).values
    )
    shuffled_accuracy = accuracy_score(y_test, model.predict(X_shuffled))

    drop = base_accuracy - shuffled_accuracy
    print(f"  Baseline accuracy:             {base_accuracy:.4f}")
    print(f"  Accuracy after shuffling:      {shuffled_accuracy:.4f}")
    print(f"  Accuracy drop:                 {drop:.4f}")

    if drop >= threshold:
        print(f"PASSED: The model relies on '{feature}' as expected.\n")
    else:
        print(f"CAUTION: Shuffling '{feature}' had little effect — "
              f"the model may not be using it.\n")


# ============================================================
# Section: Missing value handling test
# ============================================================

def test_missing_value_handling(model, X_test, num_samples=10):
    print(">>> Test: Missing Value Handling <<<")
    print("Introducing NaN values into the input to verify the pipeline "
          "handles them.\n")

    X_missing = X_test.head(num_samples).copy()

    X_missing.iloc[0, X_missing.columns.get_loc("age")] = np.nan
    X_missing.iloc[2, X_missing.columns.get_loc("monthly_income")] = np.nan
    X_missing.iloc[5, X_missing.columns.get_loc("credit_score")] = np.nan

    num_nans = X_missing.isna().sum().sum()
    print(f"Introduced {num_nans} missing values in {num_samples} test samples.")

    try:
        predictions = model.predict(X_missing)
        print("PASSED: Pipeline handled missing values without crashing.")
        print(f"  Generated {len(predictions)} predictions.")
        if np.any(np.isnan(predictions)):
            print("  WARNING: Some predictions are NaN — check imputation.")
        else:
            print("  All predictions are valid (non-NaN).")
    except Exception as e:
        print("FAILED: Pipeline crashed on missing values.")
        print(f"  Error: {type(e).__name__}: {e}")
        print("  Consider adding a SimpleImputer step to your pipeline.")


# ============================================================
# Section: Inference latency test
# ============================================================

import time

def test_inference_latency(model, X_test, max_latency_ms=100,
                           num_iterations=100):
    print(">>> Test: Inference Latency <<<")
    print(f"Testing if single-sample inference completes within "
          f"{max_latency_ms} ms.\n")

    single_sample = X_test.head(1)
    latencies = []

    for _ in range(num_iterations):
        start = time.time()
        model.predict(single_sample)
        latencies.append((time.time() - start) * 1000)

    avg = np.mean(latencies)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print(f"Single-sample latency ({num_iterations} iterations):")
    print(f"  Average: {avg:.2f} ms")
    print(f"  P95:     {p95:.2f} ms")
    print(f"  P99:     {p99:.2f} ms")

    print("\nBatch inference latency:")
    for batch_size in [10, 100, 250]:
        if batch_size <= len(X_test):
            batch = X_test.head(batch_size)
            start = time.time()
            model.predict(batch)
            total = (time.time() - start) * 1000
            per_sample = total / batch_size
            print(f"  Batch {batch_size}: {total:.2f} ms total "
                  f"({per_sample:.3f} ms/sample)")

    if p95 <= max_latency_ms:
        print(f"\nPASSED: P95 latency ({p95:.2f} ms) is within "
              f"{max_latency_ms} ms requirement.")
    else:
        print(f"\nFAILED: P95 latency ({p95:.2f} ms) exceeds "
              f"{max_latency_ms} ms requirement.")
        print("  Consider: simpler model, fewer features, or optimization.")


# ============================================================
# Section: Model regression test
# ============================================================

from sklearn.metrics import accuracy_score, f1_score

def test_model_regression(model, X_test, y_test,
                          baseline_accuracy=None,
                          min_accuracy=0.70,
                          tolerance=0.02):
    print(">>> Test: Model Regression <<<")
    print("Verifying model performance meets requirements "
          "and hasn't regressed.\n")

    predictions = model.predict(X_test)
    current_accuracy = accuracy_score(y_test, predictions)
    current_f1 = f1_score(y_test, predictions, average="weighted")

    print("Current model performance:")
    print(f"  Accuracy: {current_accuracy:.4f}")
    print(f"  F1 Score: {current_f1:.4f}")

    all_passed = True

    print(f"\n[Check 1] Minimum accuracy threshold: {min_accuracy}")
    if current_accuracy >= min_accuracy:
        print(f"  PASSED: {current_accuracy:.4f} >= {min_accuracy}")
    else:
        print(f"  FAILED: {current_accuracy:.4f} < {min_accuracy}")
        all_passed = False

    if baseline_accuracy is not None:
        print(f"\n[Check 2] Regression from baseline: "
              f"{baseline_accuracy:.4f} (tolerance: {tolerance})")
        drop = baseline_accuracy - current_accuracy
        if drop <= tolerance:
            print(f"  PASSED: Drop ({drop:.4f}) within tolerance.")
        else:
            print(f"  FAILED: Drop ({drop:.4f}) exceeds tolerance "
                  f"({tolerance}).")
            all_passed = False
    else:
        print("\n[Check 2] Baseline comparison: SKIPPED (no baseline)")
        print(f"  TIP: Save {current_accuracy:.4f} as baseline "
              f"for future tests.")

    random_baseline = max(y_test.mean(), 1 - y_test.mean())
    print(f"\n[Check 3] Better than random baseline: "
          f"{random_baseline:.4f}")
    if current_accuracy > random_baseline:
        print(f"  PASSED: Model ({current_accuracy:.4f}) beats "
              f"random ({random_baseline:.4f}).")
    else:
        print(f"  FAILED: Model ({current_accuracy:.4f}) doesn't "
              f"beat random ({random_baseline:.4f}).")
        all_passed = False

    if all_passed:
        print("\nALL REGRESSION CHECKS PASSED.")
    else:
        print("\nSOME REGRESSION CHECKS FAILED — review before deployment.")

    return current_accuracy


# --- Model testing setup: train the pipeline used by the invariance tests ---
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

NUM = ["age", "monthly_income", "credit_score", "random_noise"]
CAT = ["subscription_plan"]

X_train = train_df.drop(columns=["user_id", "will_purchase"])
y_train = train_df["will_purchase"]
X_test = test_df.drop(columns=["user_id", "will_purchase"])
y_test = test_df["will_purchase"]

numeric_transformer = make_pipeline(SimpleImputer(strategy="median"),
                                    StandardScaler())
categorical_transformer = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore"))

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, NUM),
    ("cat", categorical_transformer, CAT)])

pipeline = make_pipeline(preprocessor,
                         RandomForestClassifier(n_estimators=100,
                                                random_state=42))
pipeline.fit(X_train, y_train)
model = pipeline
