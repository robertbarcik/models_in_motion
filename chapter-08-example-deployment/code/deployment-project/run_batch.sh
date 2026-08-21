#!/bin/bash
# One batch run: fetch today's inputs, score them, publish predictions.
set -e
BUCKET=s3://mim-wine-batch
TODAY=$(date +%F)

aws s3 cp $BUCKET/incoming/$TODAY.csv incoming.csv
python batch_predict.py incoming.csv predictions.csv
aws s3 cp predictions.csv $BUCKET/predictions/$TODAY.csv
