"""1,000 flags, 100 phone calls: pick the threshold from capacity."""
import numpy as np

rng = np.random.default_rng(1)
n = 10_000
churn = rng.random(n) < 0.08
# a decent but imperfect model: churners score higher on average
score = np.clip(rng.normal(0.25, 0.15, n) + 0.35 * churn, 0, 1)

flags_default = score >= 0.5
print(f"threshold 0.50: {flags_default.sum():>4} flagged, "
      f"precision {churn[flags_default].mean():.0%}")

capacity = 100
top = np.argsort(score)[::-1][:capacity]
print(f"top {capacity} by score: threshold {score[top].min():.2f}, "
      f"precision {churn[top].mean():.0%}")
