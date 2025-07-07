from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.generate import router
from routes.guest import guest_router

app = FastAPI(title="Text2Animation")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/videos",StaticFiles(directory="outputs/videos"),name="videos")

app.include_router(router,prefix="/api")
app.include_router(guest_router,prefix="/api")