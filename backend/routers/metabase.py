from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import jwt
import time
import os

router = APIRouter()

class EmbedRequest(BaseModel):
    dashboard_id: int
    params: Optional[Dict[str, str]] = None

@router.get("/metabase/iframe-url")
def get_fixed_metabase_iframe_url():
    METABASE_SITE_URL = os.getenv("METABASE_SITE_URL")
    METABASE_SECRET_KEY = os.getenv("METABASE_SECRET_KEY")
    METABASE_DASHBOARD_ID = os.getenv("METABASE_DASHBOARD_ID")

    if not METABASE_SECRET_KEY or not METABASE_SITE_URL or not METABASE_DASHBOARD_ID:
        raise HTTPException(status_code=503, detail="Metabase config missing")

    payload = {
        "resource": {"dashboard": int(METABASE_DASHBOARD_ID)},
        "params": {},
        "exp": round(time.time()) + (60 * 10),  # 10 minutes
    }

    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
    iframe_url = f"{METABASE_SITE_URL}/embed/dashboard/{token}#theme=night&background=false&bordered=false&titled=false"
    return {"iframe_url": iframe_url}