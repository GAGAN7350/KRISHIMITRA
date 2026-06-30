$ErrorActionPreference = "Stop"

$PROJECT_ID = gcloud config get-value project
$REGION = "us-central1"
# Get integer timestamp
$TIMESTAMP = [int][double]::Parse((Get-Date -UFormat %s))
$BUCKET_NAME = "$PROJECT_ID-document-ingestion-$TIMESTAMP"
$TOPIC_NAME = "doc-upload-topic"
$DLQ_TOPIC_NAME = "doc-upload-dlq"
$SUBSCRIPTION_NAME = "doc-upload-push-sub"
$SERVICE_NAME = "doc-processor-service"
$BQ_DATASET = "document_processing"
$BQ_TABLE = "metadata"

Write-Host "Using Project: $PROJECT_ID"
Write-Host "Using Region: $REGION"

Write-Host "Creating Cloud Storage Bucket: gs://$BUCKET_NAME"
gcloud storage buckets create "gs://$BUCKET_NAME" --location=$REGION --uniform-bucket-level-access

Write-Host "Creating DLQ Topic: $DLQ_TOPIC_NAME"
gcloud pubsub topics create $DLQ_TOPIC_NAME

Write-Host "Creating Main Topic: $TOPIC_NAME"
gcloud pubsub topics create $TOPIC_NAME

Write-Host "Creating BigQuery Dataset: $BQ_DATASET"
try {
    bq mk --location=$REGION -d $BQ_DATASET
} catch {
    Write-Host "Dataset already exists or error occurred, ignoring..."
}

Write-Host "Creating BigQuery Table with daily partitioning: $BQ_DATASET.$BQ_TABLE"
try {
    bq mk --table `
      --schema "filename:STRING,date:TIMESTAMP,tags:STRING,word_count:INTEGER" `
      --time_partitioning_field date `
      --time_partitioning_type DAY `
      "$BQ_DATASET.$BQ_TABLE"
} catch {
    Write-Host "Table already exists or error occurred, ignoring..."
}

Write-Host "Deploying Cloud Run service: $SERVICE_NAME"
gcloud run deploy $SERVICE_NAME `
  --source ./src `
  --region $REGION `
  --allow-unauthenticated `
  --set-env-vars "BQ_DATASET=$BQ_DATASET,BQ_TABLE=$BQ_TABLE" `
  --quiet

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Host "Service URL: $SERVICE_URL"

Write-Host "Creating Push Subscription to Cloud Run with DLQ"
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME `
  --topic $TOPIC_NAME `
  --push-endpoint="$SERVICE_URL/" `
  --dead-letter-topic=$DLQ_TOPIC_NAME `
  --max-delivery-attempts=5

Write-Host "Configuring GCS Object Finalize notifications"
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
gcloud pubsub topics add-iam-policy-binding $TOPIC_NAME `
    --member="serviceAccount:service-$PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" `
    --role="roles/pubsub.publisher"

gcloud storage buckets update "gs://$BUCKET_NAME" --pubsub-topic="projects/$PROJECT_ID/topics/$TOPIC_NAME"

Write-Host "Pipeline Deployment Complete!"
Write-Host "Upload a file to gs://$BUCKET_NAME to trigger the pipeline."
