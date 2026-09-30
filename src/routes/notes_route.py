from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
import logging
from routes.base_route import welcome, base_router

from pathlib import Path
from controllers.NotesController import NotesController
import argostranslate.package
import argostranslate.translate
from rapidfuzz import fuzz

from routes.schemes.request import NotesRequest



logger = logging.getLogger('uvicorn.error')

notes_router = base_router

@notes_router.post("/notes_checker")
async def notes_checker(request: Request, data: NotesRequest):
    

    notes_controller= NotesController()

    is_matched = False

    benfits  = notes_controller.get_all_benefits_from_DRC_CODE(data.drc_code)

    translated_notes = notes_controller.translation(data.notes)

    # print("translated_notes: ", translated_notes)

    matches = notes_controller.find_benefit_matches(
    translated_notes,
    benfits,
    )
    
    print("matched_notes: ", matches)

    matched_benfits = set()


    for result in matches:

        for match in result["matches"]:
             matched_benfits.add(match)


    if matched_benfits:
        is_matched=True

    return JSONResponse(
            content={
                "is_matching":is_matched,
                "matched_benfits": list(matched_benfits),
                
            }
        )


