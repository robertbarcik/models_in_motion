import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier


NUMERIC_FEATURES = ["age", "monthly_spend"]
CATEGORICAL_FEATURES = ["city", "signup_source"]


def build_pipeline():
    """
    Build a complete ML pipeline with preprocessing and a classifier.

    Numeric features are imputed (median) and scaled.
    Categorical features are imputed (most frequent) and one-hot encoded.
    """
    numeric_transformer = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler()
    )
    categorical_transformer = make_pipeline(
        SimpleImputer(strategy="most_frequent"),
        OneHotEncoder(handle_unknown="ignore")
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )
    return make_pipeline(
        preprocessor,
        RandomForestClassifier(n_estimators=50, random_state=42)
    )


def save_model(model, path):
    """Save a trained pipeline to disk using joblib."""
    joblib.dump(model, path)


def load_model(path):
    """Load a trained pipeline from disk."""
    return joblib.load(path)


def preprocess_data(df):
    """
    Validate and select the expected input columns.
    Raises ValueError if any required column is missing.
    """
    expected_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    missing = set(expected_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df[expected_cols]


def predict(model, data):
    """Generate predictions using the trained pipeline."""
    return model.predict(data)