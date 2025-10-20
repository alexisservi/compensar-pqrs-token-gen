# OAuth Token Service

Cloud Run service that generates OAuth2 tokens for Google Cloud Platform authentication.

## Overview

This service provides a simple REST API to generate OAuth2 access tokens using a Service Account stored in GCP Secret Manager. It's designed for the production environment (`compensar-pqrs-prd`/`compensar-pqrs-salud`) and generates tokens with cloud-platform scope.

## Features

- **OAuth2 Token Generation**: Creates OAuth2 access tokens using Service Account credentials
- **Secret Manager Integration**: Securely retrieves Service Account keys from GCP Secret Manager
- **Health Check Endpoint**: Provides service health status monitoring
- **Cloud Run Ready**: Optimized for serverless deployment on Google Cloud Run

## API Endpoints

### `GET /get-oauth-token`
Returns an OAuth2 access token.

**Response:**
```json
{
  "status": "success",
  "token": "ya29.c.b0Aaekm1K...",
  "message": "Token OAuth2 generado exitosamente (PRODUCCIÓN)",
  "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
  "project": "compensar-pqrs-salud"
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "OAuth Token Service funcionando (PRODUCCIÓN)",
  "project": "compensar-pqrs-prd"
}
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TOKEN_GENERATION_SA` | Secret Manager path to Service Account key | `projects/PROJECT_ID/secrets/SECRET_NAME/versions/latest` |

## Local Development

### Prerequisites
- Python 3.11+
- GCP credentials with access to Secret Manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Locally
```bash
# Set environment variable
export TOKEN_GENERATION_SA="projects/.../secrets/.../versions/..."

# Run with Python
python app.py

# Or run with Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8080
```

### Test Endpoints
```bash
# Get OAuth token
curl http://localhost:8080/get-oauth-token

# Health check
curl http://localhost:8080/health
```

## Docker

### Build Image
```bash
docker build -t oauth-token-service .
```

### Run Container
```bash
docker run -p 8080:8080 \
  -e TOKEN_GENERATION_SA="projects/.../secrets/.../versions/..." \
  oauth-token-service
```

## Deployment

### Cloud Build CI/CD

The service uses Cloud Build for automated deployment:

```bash
gcloud builds submit --config cloudbuild.yaml
```

**Deployment Pipeline:**
1. Builds Docker image
2. Pushes to Artifact Registry: `us-central1-docker.pkg.dev/${PROJECT_ID}/ia-repo-servinformacion/pqrs-token-gen`
3. Deploys to Cloud Run service: `pqrs-dummy-api`

### Cloud Run Configuration

- **Service Name**: `pqrs-dummy-api`
- **Region**: `us-central1`
- **Memory**: 2Gi
- **CPU**: 2 vCPUs
- **Max Instances**: 10
- **Min Instances**: 0
- **Timeout**: 10s
- **Concurrency**: 80 requests
- **Access**: Unauthenticated

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ GET /get-oauth-token
       ▼
┌─────────────────────────┐
│  Cloud Run Service      │
│  (FastAPI)              │
│                         │
│  ┌──────────────────┐   │
│  │ Token Generator  │   │
│  └────────┬─────────┘   │
│           │             │
│           ▼             │
│  ┌──────────────────┐   │
│  │ Secret Manager   │   │
│  │ Client           │   │
│  └──────────────────┘   │
└─────────────────────────┘
           │
           │ Fetch SA Key
           ▼
┌─────────────────────────┐
│  GCP Secret Manager     │
│  (Service Account Key)  │
└─────────────────────────┘
```

## Dependencies

- **FastAPI** (0.104.1) - Web framework
- **Uvicorn** (0.24.0) - ASGI server
- **google-auth** (2.23.4) - OAuth2 token generation
- **google-cloud-secret-manager** (2.16.4) - Secret Manager access

## Project Context

- **GCP Project**: `compensar-pqrs-prd` / `compensar-pqrs-salud`
- **System**: PQRS-2025
- **Artifact Registry**: `ia-repo-servinformacion`
- **Port**: 8080

## Security Notes

- Service Account credentials are never exposed in the code
- Keys are stored securely in GCP Secret Manager
- Tokens are generated on-demand with appropriate scopes
- Service runs with minimal required permissions
