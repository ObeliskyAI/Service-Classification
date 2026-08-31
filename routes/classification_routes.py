from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
import logging
from routes.base_route import welcome, base_router

from controllers.DirectClassifyService import DirectClassifyService
from routes.schemes.request import ClassificationRequest



logger = logging.getLogger('uvicorn.error')

classsification_router = base_router

@classsification_router.post("/classify")
async def direct_classification(request: Request, data: ClassificationRequest):

    classifier = DirectClassifyService()
    results = classifier.direct_classify_service({
        "EMERGENCY": data.EMERGENCY,
        "Provider Name": data.provider_name,
        "SERVICE DESC": data.service_description
    })

    

    return JSONResponse(
            content={
                "results": results,
            }
        )


