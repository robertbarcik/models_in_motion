"""How many customers does each group need to detect a churn drop?"""
from statistics import NormalDist

z = NormalDist()
p_control = 0.080      # churn today: 8.0 % per quarter
p_treat = 0.070        # what the model must deliver to pay off: 7.0 %
alpha, power = 0.05, 0.80

z_a = z.inv_cdf(1 - alpha / 2)
z_b = z.inv_cdf(power)
p_bar = (p_control + p_treat) / 2
n = ((z_a * (2 * p_bar * (1 - p_bar)) ** 0.5
      + z_b * (p_control * (1 - p_control)
               + p_treat * (1 - p_treat)) ** 0.5) ** 2
     / (p_control - p_treat) ** 2)

print(f"customers needed in EACH group: {n:,.0f}")
