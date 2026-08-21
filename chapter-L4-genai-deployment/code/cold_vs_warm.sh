#!/usr/bin/env bash
# Time one cold invocation (after the function sat idle) and a few warm
# ones, through the public Function URL. Usage: ./cold_vs_warm.sh <url>
URL="$1"
BODY='{"prompt": "In one sentence, what is a cold start?"}'
for i in 1 2 3 4; do
  t=$(curl -s -o /dev/null -w '%{time_total}' -X POST "$URL" \
        -H 'Content-Type: application/json' -d "$BODY")
  printf 'call %d: %6.1f s\n' "$i" "$t"
done
