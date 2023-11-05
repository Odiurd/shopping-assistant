#!/bin/bash
echo "$(date +'%Y-%m-%d %H:%M:%S') - notification job started."
cd "$(dirname "$0")"
source ../venv/bin/activate
cd ../src
poetry run python notify_job.py >> ../scheduler/logs/notify_output.log 2>&1
deactivate
echo "$(date +'%Y-%m-%d %H:%M:%S') - notification job completed."
