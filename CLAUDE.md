# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Cloud Run service that generates OAuth2 tokens for Google Cloud Platform authentication. It's designed for the production environment (`compensar-pqrs-prd` project) and uses Service Account credentials stored in Secret Manager to generate OAuth2 tokens with cloud-platform scope.

## Architecture

The service is a minimal FastAPI application with two main components:

1. **Token Generation Flow** ([app.py:28-48](app.py#L28-L48))
   - Retrieves Service Account key from GCP Secret Manager using the `TOKEN_GENERATION_SA` environment variable
   - Creates credentials with `https://www.googleapis.com/auth/cloud-platform` scope
   - Refreshes and returns OAuth2 access token

2. **API Endpoints**
   - `GET /` - Returns OAuth2 token in JSON format
   - `GET /health` - Health check endpoint

## Environment Configuration

Required environment variable:
- `TOKEN_GENERATION_SA` - Secret Manager resource path for the Service Account key (format: `projects/*/secrets/*/versions/*`)

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8080
```

### Docker
```bash
# Build image
docker build -t oauth-token-service .

# Run container
docker run -p 8080:8080 -e TOKEN_GENERATION_SA="projects/.../secrets/.../versions/..." oauth-token-service
```

### Testing Endpoints
```bash
# Get token
curl http://localhost:8080/

# Health check
curl http://localhost:8080/health
```

## Deployment

### Cloud Build CI/CD

The service uses Cloud Build for automated deployment to Cloud Run ([cloudbuild.yaml](cloudbuild.yaml)):

```bash
# Trigger Cloud Build manually
gcloud builds submit --config cloudbuild.yaml
```

**Build Pipeline:**
1. Builds Docker image
2. Pushes to Artifact Registry: `us-central1-docker.pkg.dev/${PROJECT_ID}/ia-repo-servinformacion/pqrs-token-gen`
3. Deploys to Cloud Run service: `pqrs-dummy-api`

**Cloud Run Configuration:**
- Region: `us-central1`
- Memory: 2Gi
- CPU: 2
- Max instances: 10
- Min instances: 0
- Timeout: 10s
- Concurrency: 80
- Access: Unauthenticated

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- google-auth - OAuth2 token generation
- google-cloud-secret-manager - Secret Manager access

## Production Context

- Project: `compensar-pqrs-prd` / `compensar-pqrs-salud`
- Part of the PQRS-2025 system
- Deployed on Cloud Run as `pqrs-dummy-api`
- Artifact Registry: `ia-repo-servinformacion` repository
- Region: `us-central1`
- Port: 8080
