from fastapi import FastAPI, APIRouter# APIRouter is used to group routes (endpoints) together, instead of putting everything in one place
import os
from helpers import get_settings, Settings


base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/health")
async def welcome():

    return {
        "status":"Healthy"
    }