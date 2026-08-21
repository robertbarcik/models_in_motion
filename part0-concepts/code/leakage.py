"""A feature from the future makes a useless model look brilliant."""
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(0)
n = 20_000
tenure = rng.integers(1, 120, n)             # months with the bank
logins = rng.poisson(6, n)                   # logins last month
churn = rng.random(n) < 0.08                 # 8 % leave, at random
# "days since last call with retention team": recorded AFTER the
# customer announced they were leaving -> only churners have it small
retention_call = np.where(churn, rng.integers(0, 10, n),
                          rng.integers(30, 400, n))

X_honest = np.column_stack([tenure, logins])
X_leaky = np.column_stack([tenure, logins, retention_call])

for name, X in [("honest", X_honest), ("leaky ", X_leaky)]:
    Xtr, Xte, ytr, yte = train_test_split(X, churn, random_state=0)
    model = DecisionTreeClassifier(max_depth=3).fit(Xtr, ytr)
    print(f"{name} model, test accuracy: {model.score(Xte, yte):.3f}")
