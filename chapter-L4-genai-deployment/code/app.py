"""Flask web app wrapping the model - the same pattern as our ML deployment,
only the predict function now generates text instead of a number."""

import time

from flask import Flask, jsonify, request

import predict

app = Flask("genai-service")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/generate", methods=["POST"])
def generate():
    body = request.get_json(force=True)
    prompt = body.get("prompt", "")
    if not prompt:
        return jsonify({"error": "missing 'prompt'"}), 400
    max_new_tokens = int(body.get("max_new_tokens", 128))

    t0 = time.time()
    text = predict.generate(prompt, max_new_tokens=max_new_tokens)
    return jsonify({
        "response": text,
        "seconds": round(time.time() - t0, 2),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)
