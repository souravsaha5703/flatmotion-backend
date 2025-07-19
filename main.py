from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.generate import router
from routes.guest import guest_router
import os

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

OUTPUT_BASE_DIR = "outputs"

VIDEO_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, "videos")
IMAGES_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, "images")
SCRIPTS_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, "scripts")
TEX_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, "Tex")
TEXTS_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, "texts")

if not os.path.exists(OUTPUT_BASE_DIR):
    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
    print(f"Created base directory: {OUTPUT_BASE_DIR}")

for directory in [VIDEO_OUTPUT_DIR, IMAGES_OUTPUT_DIR, SCRIPTS_OUTPUT_DIR, TEX_OUTPUT_DIR, TEXTS_OUTPUT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created subdirectory: {directory}")

app.mount("/videos",StaticFiles(directory=VIDEO_OUTPUT_DIR),name="videos")

app.include_router(router,prefix="/api")
app.include_router(guest_router,prefix="/api")