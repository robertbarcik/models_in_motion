# L2 demos - execution log

Every output printed in the chapter comes from one of these runs.
Key: `source ~/.config/training-ops/openai.env`. Venv: `code/venv`
(Python 3.12.13, openai 2.48.0, tiktoken 0.14.0, pydantic 2.13.4,
httpx 0.28.1). Machine: Robert's MacBook (Apple Silicon), home Wi-Fi.

## 2026-08-20 (first draft, Claude) - 01, 02

- `python 01_first_call.py` (gpt-5.4-mini): "An ML engineer designs,
  builds, deploys, and maintains machine learning models and the
  systems that power them in real-world applications." tokens in 17,
  out 29.
- `python 02_robust_call.py`: one attempt, no retry triggered; answer
  quoted in the chapter ("your application can hang indefinitely...").
- `client.models.list()` returned 129 models that day.

## 2026-08-21 (expansion, Claude) - 03 to 06, all gpt-5.4-mini

### 03_no_memory.py - Demo A
```
turn 1 -> noted

turn 2 WITHOUT history -> I don't know your name or which cloud you use.
turn 2 WITH history    -> Your name is Jana and you use AWS.
```
(The model printed a typographic apostrophe in "don't"; normalised to
ASCII for print.)

### 04_tokens.py - Demo B (tiktoken o200k_base + one live call)
```
text      chars  tokens  chars/token
English      52      11         4.73
Slovak       54      17         3.18
Czech        49      16         3.06
JSON         76      30         2.53

reply: The model is deployed and the health check is green.
usage: prompt=31 completion=14 total=45
```

### 05_client.py - the shippable client
Normal run (`TIMEOUT` default 30 s):
```
> I was charged twice for March, please refund one payment.
   {'category': 'billing', 'urgency': 4, 'summary': 'User reports being
   charged twice for March and requests a refund for one payment.'}
> The export button does nothing since yesterday's update.
   {'category': 'bug', 'urgency': 3, 'summary': "Export button stopped
   working after yesterday's update"}
> Would be great to have dark mode in the dashboard.
   {'category': 'feature', 'urgency': 2, 'summary': 'Request for dark
   mode in the dashboard'}
meter: 3 calls, 165 in, 87 out, by model {'gpt-5.4-mini': 3}, 5.0s
```
Provoked timeout, `TIMEOUT=0.5`: every attempt timed out on every
ticket (4 attempts each, backoff 1.3/2.3/4.2/8.3 s, last attempt on the
fallback gpt-4.1-mini also timed out), all three FAILED, meter 0 calls,
54.4 s wall. NOTE for prose: the client-side meter saw nothing, but the
vendor received 12 requests and may bill for them.

Borderline, `TIMEOUT=1.5` (the one printed in the chapter):
```
> I was charged twice for March, please refund one payment.
  attempt 1 (gpt-5.4-mini): APITimeoutError, retry in 1.3s
   {'category': 'billing', 'urgency': 5, 'summary': 'Customer reports
   being charged twice for March and requests a refund for one payment.'}
> The export button does nothing since yesterday's update.
  attempt 1 (gpt-5.4-mini): APITimeoutError, retry in 1.2s
   {'category': 'bug', 'urgency': 3, 'summary': "Export button does
   nothing after yesterday's update"}
> Would be great to have dark mode in the dashboard.
  attempt 1 (gpt-5.4-mini): APITimeoutError, retry in 1.2s
  attempt 2 (gpt-5.4-mini): APITimeoutError, retry in 2.3s
  attempt 3 (gpt-5.4-mini): APITimeoutError, retry in 4.1s
  attempt 4 (gpt-4.1-mini): APITimeoutError, retry in 8.1s
   FAILED: all retries exhausted
meter: 2 calls, 110 in, 61 out, by model {'gpt-5.4-mini': 2}, 30.3s
```
Observation: urgency for the billing ticket came back 4 in one run and
5 in another - same prompt, same model. Kept in prose (non-determinism).

### 06_streaming.py - Demo C (three consecutive runs)
```
run 1  non-streaming: first visible text after 3.10s (= total), 124 words
       streaming:     first token after 0.80s, total 1.81s, 115 words
run 2  non-streaming: first visible text after 2.92s (= total), 114 words
       streaming:     first token after 2.47s, total 3.51s, 111 words
run 3  non-streaming: first visible text after 3.05s (= total), 117 words
       streaming:     first token after 0.57s, total 1.67s, 112 words
```
Run 2's slow first token (2.47 s) is real and kept as the variance note.

### Spend
~25 small calls on gpt-5.4-mini, a few hundred tokens each: well under
$0.05 total for the day (under the $1 chapter budget).

### Prices used in the two dated boxes (fetched 2026-08-21)
Source: https://developers.openai.com/api/docs/pricing (redirect target
of platform.openai.com/docs/pricing), checked by a web-research pass the
same day. gpt-5.4-mini $0.75 / $0.075 cached / $4.50 per 1M tokens;
gpt-5.4 $2.50 / $0.25 / $15.00; gpt-5.5 and the newer gpt-5.6 line
$5.00 / $0.50 / $30.00; gpt-4.1-mini fine-tuning: training $5.00 per 1M,
inference $0.80 in / $3.20 out, no hourly hosting fee stated (could not
confirm absence); gpt-5.4-mini fine-tuning not offered that day; Batch
API 50% off. Worked-example arithmetic (10k docs/day, 1500 in / 150 out,
30 days): flagship $1,800 (cached $1,260), prompted mini $378, fine-tuned
4.1-mini $312 + $30 training. The model list box in the chapter still
quotes the 2026-08-20 `models.list()` call (129 models).
