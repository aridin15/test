import os
from flask import Flask, request
import psycopg2

# 1. Import the Google Cloud Secret Manager client library
from google.cloud import secretmanager

app = Flask(__name__)

# ----------------------------------------------------
# HELPER FUNCTION: Fetch a secret version from GSM
# ----------------------------------------------------
def access_secret_version(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """
    Access the payload for the given secret version if one exists.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    # Decode the secret payload
    return response.payload.data.decode("UTF-8")

# ----------------------------------------------------
# FETCH SECRETS AT STARTUP
# ----------------------------------------------------
def fetch_db_credentials():
    """
    Fetch DB credentials from GSM. Adjust secret IDs as needed.
    The secrets must exist in GSM:
      - db-host
      - db-name
      - db-user
      - db-password
      - (optionally) db-port if you store it as well
    """
    # Adjust this to match your actual GCP Project ID
    # or rely on environment variables (e.g., os.getenv("GCP_PROJECT"))
    project_id = "<YOUR_PROJECT_ID>"

    # For demo, we assume you created these secrets:
    # gcloud secrets create db-host ...
    # gcloud secrets create db-name ...
    # gcloud secrets create db-user ...
    # gcloud secrets create db-password ...
    # and you may store db-port too, or just hardcode below.

    db_host = access_secret_version(project_id, "db-host")
    db_name = access_secret_version(project_id, "db-name")
    db_user = access_secret_version(project_id, "db-user")
    db_pass = access_secret_version(project_id, "db-password")

    # If you stored db-port in GSM, fetch it the same way,
    # otherwise hardcode or use an environment variable:
    db_port = int(os.getenv("DB_PORT", "5432"))

    return db_host, db_name, db_user, db_pass, db_port

# ----------------------------------------------------
# Initialize global variables using secrets
# ----------------------------------------------------
DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT = fetch_db_credentials()

@app.route("/write", methods=["GET"])
def write_to_db():
    try:
        # Connect to Postgres
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )

        # Create a cursor
        cur = conn.cursor()

        # Create a table if it doesn't exist yet
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        cur.execute(create_table_sql)

        # Insert a record
        insert_sql = """
        INSERT INTO test_table (content) VALUES (%s) RETURNING id;
        """
        cur.execute(insert_sql, ("Hello from Flask!",))
        record_id = cur.fetchone()[0]

        # Commit the transaction
        conn.commit()

        # Close cursor and connection
        cur.close()
        conn.close()

        return f"Successfully wrote record with ID: {record_id}", 200

    except Exception as e:
        return f"Error writing to DB: {e}", 500

@app.route("/", methods=["GET"])
def index():
    return "Hello! Use /write to write data to the database."

if __name__ == "__main__":
    # Run Flask
    app.run(host="0.0.0.0", port=8080, debug=True)
