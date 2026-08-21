import numpy as np
import json

data = {"city": "Bratislava", "temperatures": [2.1, 3.5, -1.0, 0.4, 5.2, 4.8, 3.1]}

temps = np.array(data["temperatures"])

summary = {
    "city": data["city"],
    "days": len(temps),
    "mean": round(float(np.mean(temps)), 2),
    "min": round(float(np.min(temps)), 2),
    "max": round(float(np.max(temps)), 2),
}

print(json.dumps(summary, indent=2))
