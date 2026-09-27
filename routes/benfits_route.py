from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
import logging
from routes.base_route import welcome, base_router


from controllers.BenfitsController import BenfitsController

from routes.schemes.request import BenfitsRequest



logger = logging.getLogger('uvicorn.error')

benfits_router = base_router

@benfits_router.post("/benfits_checker/benfits")
async def benfits_checker(request: Request, data: BenfitsRequest):

    benfit_detector = BenfitsController()
    results = benfit_detector.orchestrator(drc_code = data.drc_code)

    

    return JSONResponse(
            content={
                "results": results,
            }
        )


