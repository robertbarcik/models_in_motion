# L5 demo - execution log

Real, dated results of every run quoted in the chapter. Machine: Robert's
MacBook (Apple Silicon). Chapter venv: Python 3.12, pins in
`requirements.txt`. Vendor model for tool/structured demos: gpt-5.4-mini
(cheapest capable; total spend for this chapter's runs well under $0.20).
Local: Ollama with nomic-embed-text (embeddings) and qwen3:1.7b (generation).

## 2026-08-20 - original two demos (kept)

- `01_function_calling.py` - churn tool, two rounds. Output:
  `model requested: get_churn_risk({'customer_id': 'C-1001'})` then a
  recommendation quoting 0.82. Re-run 2026-08-21: same tool call, wording
  of the final answer differs slightly (as expected; sampling).
- `02_local_rag.py` - top_n=1 retrieved the CANARY snippet for the
  silent-deployment question; qwen3:1.7b then produced a fluent wrong
  answer. top_n=2 → correct. Re-run 2026-08-21: reproduces exactly
  (cosine 0.648 canary vs 0.569 silent; embeddings are deterministic).

## 2026-08-21 - expansion runs

### 01b_trace_loop.py (what goes over the wire)
Command: `source ~/.config/training-ops/openai.env && venv/bin/python
01b_trace_loop.py`. Printed the message list before each round:
round 1 = [user]; finish_reason=tool_calls; round 2 = [user, assistant
with tool_calls get_churn_risk({"customer_id":"C-1001"}), tool
{"customer_id": "C-1001", "churn_risk": 0.82}]; finish_reason=stop.
Final: "Customer C-1001 has a churn risk of 0.82, which is high. Yes - it
would be a good candidate for a retention offer."

### Demo A - 03_tool_calls_part1_app.py (LLM tool → Part 1 Flask app)
Part 1 wine app started from a COPY of
`part1-ml-models/chapter-10-example-deployment/code/deployment-project/`
in the scratchpad (venv from its own requirements.txt on Python 3.12;
scikit-learn 1.6.1, Flask 3.1.0 installed fine), `python predict.py`,
port 9696. Part 1 files untouched. Smoke test by curl: `[5.12]`.
Run: model requested predict_wine_quality with all 11 numbers from the
prose; tool POSTed `[[7.4, 0.7, 0, ...]]`; Flask log shows
`POST /predict HTTP/1.1 200`; Part 1 answered 5.12; model wrote a
"middling, table-worthy but not a showpiece" answer and commented on
volatile acidity 0.7 and alcohol 9.4 (its own chemistry, not the model's).
Note: the Flask log also holds two 500s ("X has 4 features, but
MinMaxScaler is expecting 11") from an early manual curl while I was
starting the app - not from the LLM demo.

### 03b_partial_measurements.py (the honest edge case)
User gives only 4 of 11 measurements.
- plain description: finish_reason=tool_calls, model INVENTED the other
  seven (fixed_acidity 7, citric_acid 0.3, residual_sugar 2.5, chlorides
  0.08, free SO2 15/20, total SO2 45/60, density 0.996 - plausible
  "typical red wine" values). Reproduced twice (values varied slightly).
- `--strict` (one sentence added to the tool description: never guess,
  ask): finish_reason=stop, model listed the 11 required values and asked
  for the missing 7. No tool call.

### Demo B - 04_structured_output.py (pydantic-validated extraction)
`client.chat.completions.parse(response_format=Ticket)`.
- `Ticket` (order_id: str required + regex validator): API returned a
  schema-valid object but `order_id` was `''` (the email has no order
  number). Pydantic: `VALIDATION FAILED: Value error, order_id '' is not
  ORD-123456 shaped`. Reproduced twice.
- `TicketV2` (order_id Optional, description says "or null if not in the
  text"): `{"customer_name": "Petra Novak", "order_id": null, "issue":
  "wrong_item", "sentiment": "angry", "wants_refund": true, "phone":
  "+421 905 000 111"}`.

### Demo C - 05_rag_eval.py (retrieval evaluated on its own, local)
12 passages, 8 questions with one gold doc each, nomic-embed-text,
cosine on normalised vectors. ~2 s per run. Results (hit@1 / hit@3):
- baseline (one passage per chunk)   0.750 / 1.000
- title prefix ("Canary deployment: ...")   0.750 / 0.875
- embedder task prefixes (search_document:/search_query:)  0.750 / 0.875
- paired passages (bigger chunks, 6 candidates)  0.875 / 1.000
Per-question baseline: misses are Q1 (silent deployment; canary ranked
1, silent 2, registry 3) and Q3 (control group ranked 3 behind data
drift 0.566 and cold start 0.547; control group 0.530).
Caveat recorded in chapter: the paired-chunk score is flattering because
the candidate set halved and the "correct" chunk now carries two topics
(canary+silent in the same chunk) - the ambiguity moved from retrieval
to generation.

### Demo D - 06_mcp_server.py + 07_mcp_client.py + 07b_mcp_raw_wire.py
mcp SDK 2.0.0: the server class is `mcp.server.mcpserver.MCPServer`
(the 1.x name `FastMCP` / module `mcp.server.fastmcp` no longer
imports - first attempt failed with ModuleNotFoundError; second attempt
failed on `Tool.inputSchema` → 2.0 uses `input_schema`). Both noted in
the chapter's dated box.
- 07 (SDK client over stdio): server name churn-model; tool
  get_churn_risk with schema ['customer_id']; resource churn://model-card
  readable; call_tool → {"customer_id": "C-1001", "churn_risk": 0.82}.
- 07b (raw JSON-RPC over the subprocess pipe, no SDK): initialize →
  notifications/initialized → tools/call for C-1002 → result content
  text {"customer_id": "C-1002", "churn_risk": 0.11}, isError false.

## Cleanup
Wine Flask app stopped after the runs; scratchpad copy is throwaway.
No cloud resources used in this chapter.

### 2026-08-21, later - re-runs after tidying
- `03_tool_calls_part1_app.py` TOOLS rewritten to the compact form shown
  in print; re-run: identical tool call, Part 1 answered 5.12 again.
- `03b_partial_measurements.py` plain, third run: invented again
  (citric_acid 0.2, residual_sugar 2, total SO2 40 this time).

## 2026-09-17 - round-3 re-run of 04_structured_output.py (phone number changed)
Jana's review (item 3.67): `+421 905 000 111` could belong to a real person.
EMAIL in the script now uses `+44 7700 900 123`, from the range Ofcom
reserves for drama and never assigns. Nothing else in the script changed.
Command: `source ~/.config/training-ops/openai.env && venv/bin/python
04_structured_output.py`, run twice, same venv, gpt-5.4-mini. Both runs
identical:
- `Ticket`: `VALIDATION FAILED: Value error, order_id '' is not ORD-123456
  shaped` / `model had returned: ''` (same as 2026-08-21).
- `TicketV2`: `{"customer_name": "Petra Novak", "order_id": null, "issue":
  "wrong_item", "sentiment": "angry", "wants_refund": true, "phone":
  "+44 7700 900 123"}`. Only the phone field differs from the August run.
The chapter now prints the e-mail itself and this output.
