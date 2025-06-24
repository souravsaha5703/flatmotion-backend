from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.generate import router

app = FastAPI(title="Text2Animation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/videos",StaticFiles(directory="outputs/videos"),name="videos")

app.include_router(router,prefix="/api")