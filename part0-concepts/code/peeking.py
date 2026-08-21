"""What happens if we stop the experiment the first time it looks good."""
import random
from statistics import NormalDist

random.seed(42)
z = NormalDist()
p = 0.08                       # SAME churn in both groups: no real effect
n_total, checks, runs = 12_000, 12, 2_000


def significant(c, t, n):
    p_bar = (c + t) / (2 * n)
    se = (2 * p_bar * (1 - p_bar) / n) ** 0.5
    return abs(c - t) / n / se > z.inv_cdf(0.975) if se else False


once = peeked = 0
for _ in range(runs):
    ctrl = [random.random() < p for _ in range(n_total)]
    trt = [random.random() < p for _ in range(n_total)]
    once += significant(sum(ctrl), sum(trt), n_total)
    for k in range(1, checks + 1):           # look every 1,000 customers
        n = n_total * k // checks
        if significant(sum(ctrl[:n]), sum(trt[:n]), n):
            peeked += 1
            break

print(f"false alarms, one look at the end : {once / runs:.1%}")
print(f"false alarms, stop at first 'win'  : {peeked / runs:.1%}")
