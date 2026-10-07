# ============================================================
# Bonus: Generating pipelines with TPOT
# Run this code in a Jupyter notebook.
# Install first: pip install tpot==1.1.0
# ============================================================


# ============================================================
# Section: Creating a synthetic dataset
# ============================================================

import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

# Generate synthetic regression data
X, y = make_regression(
    n_samples=500,
    n_features=10,
    n_informative=5,      # Only 5 features actually matter
    noise=20,             # Add some noise to make it realistic
    random_state=42
)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training samples: {X_train.shape[0]}")
print(f"Test samples: {X_test.shape[0]}")
print(f"Features: {X_train.shape[1]}")


# ============================================================
# Section: Running the genetic search
# ============================================================

from tpot import TPOTRegressor

# Initialize TPOT with conservative settings
tpot = TPOTRegressor(
    generations=5,
    population_size=20,
    cv=5,                    # 5-fold cross-validation
    max_time_mins=None,      # Use generations as the only stopping criterion
    verbose=2,               # Show progress
    random_state=42,
    n_jobs=1                 # Sequential execution
)

# Run the optimization
print("Starting TPOT optimization...")
tpot.fit(X_train, y_train)


# ============================================================
# Section: Analyzing the winning pipeline
# ============================================================

from sklearn.metrics import mean_squared_error, r2_score

# The best pipeline found by TPOT is accessible via fitted_pipeline_
best_pipeline = tpot.fitted_pipeline_

# Make predictions on the test set
y_pred = best_pipeline.predict(X_test)

# Evaluate using standard sklearn metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nTest set MSE: {mse:.4f}")
print(f"Test set R²: {r2:.4f}")

# Inspect the pipeline structure
print(tpot.fitted_pipeline_)

# Iterate through steps for full detail
for name, step in tpot.fitted_pipeline_.steps:
    print(f"Step: {name}")
    print(f"  {step}")
    print()


# ============================================================
# Section: Serializing the best pipeline for deployment
# ============================================================

import dill as pickle

# Save the fitted pipeline
with open("best_pipeline.pkl", "wb") as f:
    pickle.dump(tpot.fitted_pipeline_, f)

# Later, in production API or app, you can load it
with open("best_pipeline.pkl", "rb") as f:
    loaded_pipeline = pickle.load(f)

# Use it directly - no retraining needed or tpot search required
predictions = loaded_pipeline.predict(X_test)


# ============================================================
# Section: Exporting to clean code
# ============================================================

import re

def export_pipeline_code(pipeline):
    """Generate standalone Python code from a fitted sklearn pipeline."""

    def collect_imports(estimator, imports_set):
        """Recursively collect imports from an estimator and its nested components."""
        cls = type(estimator)
        module_parts = cls.__module__.split('.')
        public_module = '.'.join(p for p in module_parts if not p.startswith('_'))
        imports_set.add(f"from {public_module} import {cls.__name__}")

        # Recurse into nested estimators (e.g., RFE contains ExtraTreesRegressor)
        if hasattr(estimator, 'get_params'):
            for param_value in estimator.get_params(deep=False).values():
                if hasattr(param_value, 'get_params'):
                    collect_imports(param_value, imports_set)
                elif isinstance(param_value, list):
                    for item in param_value:
                        if isinstance(item, tuple):
                            for element in item:
                                if hasattr(element, 'get_params'):
                                    collect_imports(element, imports_set)

    imports = set()
    imports.add("from sklearn.pipeline import make_pipeline")
    step_reprs = []

    for name, step in pipeline.steps:
        collect_imports(step, imports)

        # Get constructor representation and clean up numpy wrappers
        step_code = repr(step)
        step_code = step_code.replace("np.True_", "True")
        step_code = step_code.replace("np.False_", "False")
        step_code = re.sub(r"np\.str_\('([^']*)'\)", r"'\1'", step_code)
        step_reprs.append(step_code)

    # Print the generated code
    for imp in sorted(imports):
        print(imp)
    print()
    print("pipeline = make_pipeline(")
    for step_code in step_reprs:
        lines = step_code.split('\n')
        for j, line in enumerate(lines):
            if j == len(lines) - 1:
                print(f"    {line},")    # Comma after each step's closing parenthesis
            else:
                print(f"    {line}")
    print()
    print(")")
    print()
    print("pipeline.fit(X_train, y_train)")
    print("predictions = pipeline.predict(X_test)")

export_pipeline_code(tpot.fitted_pipeline_)


# ============================================================
# Section: Evaluating alternatives
# ============================================================

print(f"Total pipelines evaluated: {len(tpot.evaluated_individuals)}")
tpot.evaluated_individuals.head()

# Retrieve the second-best pipeline
sorted_pipelines = tpot.evaluated_individuals.sort_values('mean_squared_error', ascending=False)
second_best_pipeline = sorted_pipelines.iloc[1]['Instance']
print(second_best_pipeline)
