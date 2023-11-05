#!/bin/bash
echo "$(date +'%Y-%m-%d %H:%M:%S') - database backup to GCS started."
cd "$(dirname "$0")"
cd ../src/database
gsutil cp shopping_notification.db gs://shopping-notification/database/shopping_notification.db
echo "$(date +'%Y-%m-%d %H:%M:%S') - database backup to GCS completed."
