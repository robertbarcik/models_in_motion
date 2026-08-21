import numpy as np
import pandas as pd
from my_pipeline import build_pipeline, save_model, load_model, preprocess_data, predict


def test_full_pipeline(tmp_path):

    # -- Arrange: prepare training data and sample input ----------------

    train_data = pd.DataFrame({
        "age":           [25, 40, 55, 30, 45, 60, 22, 38, 50, 28],
        "city":          ["London", "Paris", "New York", "London", "Paris",
                          "New York", "London", "Paris", "New York", "London"],
        "monthly_spend": [50.0, 80.0, 120.0, 45.0, 90.0,
                          110.0, 55.0, 75.0, 130.0, 40.0],
        "signup_source": ["Organic", "Referral", "Paid", "Organic", "Referral",
                          "Paid", "Organic", "Referral", "Paid", "Organic"],
    })
    train_labels = np.array([0, 1, 1, 0, 1, 1, 0, 1, 1, 0])

    sample_input = pd.DataFrame({
        "age":           [25, 40, 90],
        "city":          ["London", "Paris", "New York"],
        "monthly_spend": [50.0, 80.0, 120.0],
        "signup_source": ["Organic", "Referral", "Paid"],
    })

    model_path = tmp_path / "test_model.joblib"

    # -- Act: build, train, save, load, and predict ---------------------

    pipeline = build_pipeline()
    pipeline.fit(preprocess_data(train_data), train_labels)
    save_model(pipeline, model_path)

    loaded_model = load_model(model_path)
    processed_input = preprocess_data(sample_input)
    preds = predict(loaded_model, processed_input)

    # -- Assert: validate predictions -----------------------------------

    assert preds.shape[0] == sample_input.shape[0], \
        "Number of predictions must match number of input rows"

    assert isinstance(preds, np.ndarray), \
        "Predictions should be a numpy array"

    assert set(preds).issubset({0, 1}), \
        "All predictions must be valid class labels (0 or 1)"

    assert processed_input.shape[0] == sample_input.shape[0], \
        "Preprocessing must not silently drop any rows"