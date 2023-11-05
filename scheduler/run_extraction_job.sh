#!/bin/bash
echo "$(date +'%Y-%m-%d %H:%M:%S') - extraction job started."
cd "$(dirname "$0")"
source ../venv/bin/activate
cd ../src
poetry run python extraction_job.py >> ../scheduler/logs/extraction_output.log 2>&1
deactivate
echo "$(date +'%Y-%m-%d %H:%M:%S') - extraction job completed."
