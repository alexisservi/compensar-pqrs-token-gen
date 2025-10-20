#!/usr/bin/env python3
"""
Cloud Run Service para generar tokens OAuth2 de Google Cloud (PRODUCCIÓN)
Basado en el JWT service pero adaptado para tokens OAuth2
Proyecto: compensar-pqrs-prd
"""

import json
import google.auth.transport.requests
from google.oauth2 import service_account
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google.cloud import secretmanager
import os

app = FastAPI(title="OAuth Token Service (PRD)", version="1.0.0")

def get_sa_key_from_secret_manager():
    """Obtiene la clave del Service Account desde Secret Manager (PRODUCCIÓN)"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = os.environ["TOKEN_GENERATION_SA"]
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        raise Exception(f"Error obteniendo SA key desde Secret Manager (PRD): {str(e)}")

def generate_oauth_token():
    """Genera un token OAuth2 usando la Service Account de producción"""
    try:
        # Obtener SA key desde Secret Manager (PRODUCCIÓN)
        sa_key_json = get_sa_key_from_secret_manager()
        sa_key_data = json.loads(sa_key_json)
        
        # Crear credenciales desde la información de la SA
        credentials = service_account.Credentials.from_service_account_info(
            sa_key_data, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Refrescar el token
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        return credentials.token
        
    except Exception as e:
        raise Exception(f"Error generando token OAuth2 (PRD): {str(e)}")

@app.get("/api/get-oauth-token")
async def get_oauth_token():
    """Endpoint principal que devuelve el token OAuth2"""
    try:
        token = generate_oauth_token()
        return JSONResponse({
            "status": "success",
            "token": token,
            "message": "Token OAuth2 generado exitosamente",
            "scopes": ['https://www.googleapis.com/auth/cloud-platform'],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando token: {str(e)}")

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {"status": "ok", "message": "OAuth Token Service funcionando (PRODUCCIÓN)", "project": "compensar-pqrs-prd"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
