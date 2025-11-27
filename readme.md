# Raise Your Votes

A minimal FastAPI scaffold for a simple voting app where users can post positions and add a single vote. The app is containerized for Cloud Run with a Cloud Build pipeline.

## Running locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API and web UI:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Visit [http://localhost:8000](http://localhost:8000) to create positions and add votes.

Persistent storage defaults to a SQLite database located in `data/app.db`. To use a more
durable database (for example, Postgres), set `DATABASE_URL` before starting the server,
using any SQLAlchemy-supported URL such as:

```bash
export DATABASE_URL="postgresql+psycopg2://dbuser:dbpass@dbhost:5432/raiseyourstakes"
uvicorn app.main:app --reload
```

For Cloud SQL (Postgres) on Cloud Run, set the following variables and let the app
construct the SQLAlchemy URL for you:

```bash
export CLOUD_SQL_CONNECTION_NAME="amazing-jetty-460321-v0:europe-west1:free-trial-first-project"
export DB_USER="dbuser"
export DB_PASSWORD="dbpass"
export DB_NAME="raiseyourstakes"
# Optional: override the Unix socket host path if you mount a custom socket directory.
# export DB_HOST="/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"

uvicorn app.main:app --reload
```

## Docker

Build and run locally:

```bash
docker build -t raiseyourstakes .
docker run -p 8080:8080 raiseyourstakes
```

## Cloud Build + Cloud Run

`cloudbuild.yaml` builds and deploys to Cloud Run:

- Builds and pushes `gcr.io/$PROJECT_ID/raiseyourstakes`.
- Deploys the image to Cloud Run in the region specified by the `_REGION` substitution (default `us-central1`).

Trigger the build from the repo root:

```bash
gcloud builds submit --substitutions=_REGION=us-central1
```
