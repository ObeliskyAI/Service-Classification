from fastapi import FastAPI
from controllers.BaseController import BaseController
from controllers.DirectClassifyService import DirectClassifyService
from controllers.BenfitsController import BenfitsController
from routes import classification_routes , base_route, benfits_route



app = FastAPI()

app.include_router(base_route.base_router)
app.include_router(classification_routes.classsification_router)
app.include_router(benfits_route.benfits_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)