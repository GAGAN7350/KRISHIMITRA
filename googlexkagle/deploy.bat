@echo off
setlocal enabledelayedexpansion

REM Configuration variables
FOR /F "tokens=*" %%g IN ('gcloud config get-value project') do (SET PROJECT_ID=%%g)
set REGION=us-central1
set BUCKET_NAME=%PROJECT_ID%-document-ingestion-%RANDOM%
set TOPIC_NAME=doc-upload-topic
set DLQ_TOPIC_NAME=doc-upload-dlq
set SUBSCRIPTION_NAME=doc-upload-push-sub
set SERVICE_NAME=doc-processor-service
set BQ_DATASET=document_processing
set BQ_TABLE=metadata

echo Using Project: %PROJECT_ID%
echo Using Region: %REGION%

echo Creating Cloud Storage Bucket: gs://%BUCKET_NAME%
call gcloud storage buckets create gs://%BUCKET_NAME% --location=%REGION% --uniform-bucket-level-access

echo Creating DLQ Topic: %DLQ_TOPIC_NAME%
call gcloud pubsub topics create %DLQ_TOPIC_NAME%

echo Creating Main Topic: %TOPIC_NAME%
call gcloud pubsub topics create %TOPIC_NAME%

echo Creating BigQuery Dataset: %BQ_DATASET%
call bq mk --location=%REGION% -d %BQ_DATASET%

echo Creating BigQuery Table with daily partitioning: %BQ_DATASET%.%BQ_TABLE%
call bq mk --table --schema "filename:STRING,date:TIMESTAMP,tags:STRING,word_count:INTEGER" --time_partitioning_field date --time_partitioning_type DAY %BQ_DATASET%.%BQ_TABLE%

echo Deploying Cloud Run service: %SERVICE_NAME%
call gcloud run deploy %SERVICE_NAME% --source ./src --region %REGION% --allow-unauthenticated --set-env-vars BQ_DATASET=%BQ_DATASET%,BQ_TABLE=%BQ_TABLE% --quiet

FOR /F "tokens=*" %%g IN ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format="value(status.url)"') do (SET SERVICE_URL=%%g)
echo Service URL: %SERVICE_URL%

echo Creating Push Subscription to Cloud Run with DLQ
call gcloud pubsub subscriptions create %SUBSCRIPTION_NAME% --topic %TOPIC_NAME% --push-endpoint="%SERVICE_URL%/" --dead-letter-topic=%DLQ_TOPIC_NAME% --max-delivery-attempts=5

echo Configuring GCS Object Finalize notifications
FOR /F "tokens=*" %%g IN ('gcloud projects describe %PROJECT_ID% --format="value(projectNumber)"') do (SET PROJECT_NUMBER=%%g)
call gcloud pubsub topics add-iam-policy-binding %TOPIC_NAME% --member="serviceAccount:service-%PROJECT_NUMBER%@gs-project-accounts.iam.gserviceaccount.com" --role="roles/pubsub.publisher"

call gcloud storage buckets update gs://%BUCKET_NAME% --pubsub-topic=projects/%PROJECT_ID%/topics/%TOPIC_NAME%

echo Pipeline Deployment Complete!
echo Upload a file to gs://%BUCKET_NAME% to trigger the pipeline.
