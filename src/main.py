from fastapi import FastAPI
from routes import classification_routes , base_route, benfits_route,notes_route



app = FastAPI()

app.include_router(base_route.base_router)
app.include_router(classification_routes.classsification_router)
app.include_router(benfits_route.benfits_router)
app.include_router(notes_route.notes_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)