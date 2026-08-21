"""AWS Lambda handler. The model loads at import time (the cold start),
so warm invocations only pay for generation."""

import json
import time

import predict


def handler(event, context):
    # A Function URL delivers the HTTP body as a JSON string
    body = event.get("body") or "{}"
    if isinstance(body, str):
        body = json.loads(body)

    prompt = body.get("prompt", "")
    if not prompt:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "missing 'prompt'"}),
        }

    t0 = time.time()
    text = predict.generate(prompt, max_new_tokens=int(body.get("max_new_tokens", 128)))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "response": text,
            "seconds": round(time.time() - t0, 2),
        }),
    }
