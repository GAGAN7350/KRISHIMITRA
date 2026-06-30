#!/bin/bash
# Serverless Document Processing Pipeline Setup Script

# Exit immediately if a command exits with a non-zero status.
set -e

# Configuration variables (modify these as needed)
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
BUCKET_NAME="${PROJECT_ID}-document-ingestion-$(date +%s)"
TOPIC_NAME="doc-upload-topic"
DLQ_TOPIC_NAME="doc-upload-dlq"
SUBSCRIPTION_NAME="doc-upload-push-sub"
SERVICE_NAME="doc-processor-service"
BQ_DATASET="document_processing"
BQ_TABLE="metadata"

echo "Using Project: $PROJECT_ID"
echo "Using Region: $REGION"

# 1. Create Cloud Storage Bucket
echo "Creating Cloud Storage Bucket: gs://$BUCKET_NAME"
gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION --uniform-bucket-level-access

# 2. Create Pub/Sub Topics
echo "Creating DLQ Topic: $DLQ_TOPIC_NAME"
gcloud pubsub topics create $DLQ_TOPIC_NAME

echo "Creating Main Topic: $TOPIC_NAME"
gcloud pubsub topics create $TOPIC_NAME

# 3. Create BigQuery Dataset and Table
echo "Creating BigQuery Dataset: $BQ_DATASET"
bq mk --location=$REGION -d $BQ_DATASET || true # Ignore error if already exists

echo "Creating BigQuery Table with daily partitioning: $BQ_DATASET.$BQ_TABLE"
# Schema: filename:STRING, date:TIMESTAMP, tags:STRING, word_count:INTEGER
bq mk --table \
  --schema "filename:STRING,date:TIMESTAMP,tags:STRING,word_count:INTEGER" \
  --time_partitioning_field date \
  --time_partitioning_type DAY \
  $BQ_DATASET.$BQ_TABLE || true # Ignore error if already exists

# 4. Deploy Cloud Run Service
echo "Deploying Cloud Run service: $SERVICE_NAME"
# Note: we need to use 'gcloud run deploy' pointing to the src directory.
gcloud run deploy $SERVICE_NAME \
  --source ./src \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars BQ_DATASET=$BQ_DATASET,BQ_TABLE=$BQ_TABLE \
  --quiet

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"

# 5. Create Pub/Sub Push Subscription with DLQ
echo "Creating Push Subscription to Cloud Run with DLQ"
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
  --topic $TOPIC_NAME \
  --push-endpoint="$SERVICE_URL/" \
  --dead-letter-topic=$DLQ_TOPIC_NAME \
  --max-delivery-attempts=5

# 6. Configure GCS notifications to Pub/Sub
echo "Configuring GCS Object Finalize notifications"
# Give Cloud Storage permission to publish to Pub/Sub
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud pubsub topics add-iam-policy-binding $TOPIC_NAME \
    --member="serviceAccount:service-$PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

gcloud storage buckets update gs://$BUCKET_NAME --pubsub-topic=projects/$PROJECT_ID/topics/$TOPIC_NAME

echo "Pipeline Deployment Complete!"
echo "Upload a file to gs://$BUCKET_NAME to trigger the pipeline."
