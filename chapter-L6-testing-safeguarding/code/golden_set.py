"""The golden set: ten factual prompts with a short expected answer
and a permissive regex. Deliberately small and hand-checkable - a real
suite grows from your incident log, but the shape is exactly this."""

GOLDEN = [
    {"prompt": "What is the capital of France? Answer in one word.",
     "expected": "Paris", "regex": r"\bparis\b"},
    {"prompt": "Chemical symbol for gold? Symbol only.",
     "expected": "Au", "regex": r"\bAu\b"},
    {"prompt": "How many continents are there? A number.",
     "expected": "7 (seven)", "regex": r"\b(7|seven)\b"},
    {"prompt": "Who wrote Romeo and Juliet? Name only.",
     "expected": "Shakespeare", "regex": r"shakespeare"},
    {"prompt": "Boiling point of water at sea level in Celsius? "
               "Number only.",
     "expected": "100", "regex": r"\b100\b"},
    {"prompt": "Which planet is called the Red Planet? One word.",
     "expected": "Mars", "regex": r"\bmars\b"},
    {"prompt": "In what year did World War II end? Year only.",
     "expected": "1945", "regex": r"\b1945\b"},
    {"prompt": "Largest ocean on Earth? Name only.",
     "expected": "Pacific", "regex": r"pacific"},
    {"prompt": "What gas do plants absorb for photosynthesis?",
     "expected": "carbon dioxide (CO2)",
     "regex": r"carbon dioxide|\bco2\b"},
    {"prompt": "What is the square root of 144? Number only.",
     "expected": "12", "regex": r"\b12\b"},
]
