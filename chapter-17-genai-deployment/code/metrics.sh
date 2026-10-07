#!/usr/bin/env bash
# Two days of Lambda metrics for the deployed function, one row per day.
FN=mim-genai-demo
START=$(date -u -v-2d +%Y-%m-%dT00:00:00Z 2>/dev/null \
        || date -u -d '2 days ago' +%Y-%m-%dT00:00:00Z)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for METRIC in Invocations Duration; do
  echo "== $METRIC"
  aws cloudwatch get-metric-statistics --namespace AWS/Lambda \
    --metric-name "$METRIC" --dimensions Name=FunctionName,Value=$FN \
    --start-time "$START" --end-time "$END" --period 86400 \
    --statistics Sum Average Maximum \
    --query 'sort_by(Datapoints,&Timestamp)[].[Timestamp,Sum,Average,Maximum]' \
    --output table
done
