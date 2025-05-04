# api/routes.py
import logging
import os  # Move os import up
import json  # Move json import up
from typing import Dict  # Move typing import up

# --- Configure logging FIRST ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# --- End logging config ---

from fastapi import FastAPI, HTTPException, Depends  # Import Depends
from fastapi.responses import StreamingResponse, JSONResponse

# Import settings and the dependency function
from core.config import Settings, get_settings

# Import the storm runner function
from core.gemini_storm_integration import run_storm
from api.models import StormRequest
from utils.chunks import chunk_string

# Remove manual dotenv loading - handled by core.config now

app = FastAPI()


@app.post("/storm")
# Inject settings using Depends
async def storm_endpoint(
    request: StormRequest, settings: Settings = Depends(get_settings)
):
    """
    Run STORM for the given topic using injected settings.
    If stream is False, return JSON; if True, stream the JSON response.
    """
    topic = request.topic
    stream = request.stream

    if not topic:
        raise HTTPException(status_code=400, detail="Topic must be a non-empty string")

    logger.info(f"Received request: topic='{topic}', stream={stream}")

    # Get API keys from injected settings
    google_key = settings.google_api_key
    serper_key = settings.serper_api_key

    if not google_key:
        logger.error("GOOGLE_API_KEY not found in loaded settings.")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: GOOGLE_API_KEY is not configured.",
        )
    if not serper_key:
        logger.error("SERPER_API_KEY not found in loaded settings.")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: SERPER_API_KEY is not configured.",
        )

    try:
        # Invoke the STORM pipeline, passing both API keys from settings
        result = run_storm(
            topic=topic, google_api_key=google_key, serper_api_key=serper_key
        )
    except ValueError as ve:  # Catch potential errors from run_storm (e.g., empty keys)
        logger.error(f"STORM configuration or execution error: {ve}")
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Error running STORM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # If run_storm returned a dict, we assume it has the final data (but our impl returns str)
    if isinstance(result, dict):
        response_data = result
    else:
        # Wrap string result in JSON format
        response_data = {"article": result}

    if not stream:
        # Return full JSON response
        return JSONResponse(content=response_data)

    # Otherwise, stream the response in chunks
    json_str = json.dumps(response_data)

    def iter_json():
        # Stream the JSON string in fixed-size chunks
        for chunk in chunk_string(json_str, 1024):
            yield chunk

    return StreamingResponse(iter_json(), media_type="application/json")
