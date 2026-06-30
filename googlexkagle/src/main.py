import os
import json
import base64
import random
from datetime import datetime
from flask import Flask, request
from google.cloud import bigquery

app = Flask(__name__)

BQ_DATASET = os.environ.get('BQ_DATASET', 'document_processing')
BQ_TABLE = os.environ.get('BQ_TABLE', 'metadata')

# Initialize BigQuery client
bq_client = bigquery.Client()

@app.route('/', methods=['POST'])
def process_message():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope['message']

    if isinstance(pubsub_message, dict) and 'data' in pubsub_message:
        try:
            data = base64.b64decode(pubsub_message['data']).decode('utf-8')
            event_payload = json.loads(data)
            
            # GCS notification event payload contains 'name' (filename) and 'bucket'
            filename = event_payload.get('name', 'unknown_file')
            bucket = event_payload.get('bucket', 'unknown_bucket')
            
            print(f"Processing file: {filename} from bucket: {bucket}")
            
            # Simulated OCR and metadata extraction
            extracted_tags = ["invoice", "receipt", "confidential", "draft", "approved", "w2", "tax", "report"]
            random_tags = random.sample(extracted_tags, k=random.randint(1, 3))
            tags_str = ",".join(random_tags)
            word_count = random.randint(100, 5000)
            
            # Prepare row for BigQuery
            row_to_insert = [
                {
                    "filename": filename,
                    "date": datetime.utcnow().isoformat(),
                    "tags": tags_str,
                    "word_count": word_count
                }
            ]
            
            # Insert into BigQuery
            table_id = f"{bq_client.project}.{BQ_DATASET}.{BQ_TABLE}"
            errors = bq_client.insert_rows_json(table_id, row_to_insert)
            
            if errors == []:
                print(f"New rows have been added for {filename}.")
            else:
                print(f"Encountered errors while inserting rows: {errors}")
                # We return 500 so Pub/Sub retries and eventually goes to DLQ
                return "Internal Server Error", 500

        except Exception as e:
            print(f"Error processing message: {e}")
            return "Internal Server Error", 500

    return ("", 204)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=PORT)
