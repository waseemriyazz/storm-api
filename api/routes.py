
import logging
import json

from fastapi import FastAPI, HTTPException, Depends 
from fastapi.responses import StreamingResponse, JSONResponse

from utils.exception_handler import http_exception_handler  
from core.config import Settings, get_settings
from core.gemini_storm_integration import run_storm
from api.models import ArticleData, ErrorResponse, StormData, StormRequest, StormResponse
from utils.chunks import iter_json_dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI()
app.add_exception_handler(HTTPException, http_exception_handler)


@app.post("/storm", response_model=StormResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)

async def storm_endpoint(
    request: StormRequest, settings: Settings = Depends(get_settings)
):
    """
    Run STORM for the given topic using injected settings.
    If stream is False, return JSON; if True, stream the JSON response.
    """
    topic =  request.topic.strip()
    stream = request.stream

    if not topic:
        raise HTTPException(status_code=400, detail="Topic must be a non-empty string")

    logger.info(f"Received request: topic='{topic}', stream={stream}")

   
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
        
        result :ArticleData = run_storm(
            topic=topic, google_api_key=google_key, serper_api_key=serper_key
        )
    except ValueError as ve:  
        logger.error(f"STORM configuration or execution error: {ve}")
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Error running STORM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    storm_data = StormData(result)
    if not stream:
        return StormResponse(status_code=200, data=storm_data.model_dump())


    
    return StreamingResponse(
        iter_json_dict(storm_data.model_dump()), media_type="application/json"
    )