from fastapi import APIRouter,HTTPException
from models.prompt import PromptRequest
from config import client
from services.utils import save_script,get_video_url,render_video
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

@router.post("/generate")
async def generate_animation(req:PromptRequest):
    print(req.prompt)
    try:
        completion = client.chat.completions.create(
            model="provider-5/gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": os.getenv("API_CONTENT")
                },
                {
                    "role": "user",
                    "content": req.prompt
                }
            ],
            temperature=0.7,
            max_tokens=600,
        )
        if completion.choices and completion.choices[0].message.content:
            script = completion.choices[0].message.content
            if script.startswith("```"):
                script = script.strip("`").strip()
                if script.startswith("python"):
                    script = script[len("python"):].strip()
            script_path = save_script(script)
            rendered_video = render_video(script_path)
            video_path = get_video_url(rendered_video)
            return video_path
        else:
            raise HTTPException(status_code=500, detail="Failed to generate Manim script: No content received.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during script generation: {str(e)}")