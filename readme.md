# Raise Your Stakes

A minimal FastAPI scaffold for a betting-style app where users can post positions and vote with a stake. The app is containerized for Cloud Run with a Cloud Build pipeline.

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

Persistent storage uses a SQLite database located in `data/app.db`.

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
