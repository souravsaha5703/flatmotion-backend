from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.prompt import PromptRequest
from models.error_response import ErrorResponse
from config import client
from services.utils import save_script,get_video_url,render_video,calculate_max_tokens
from services.validation import validate_prompt
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

@router.post("/generate")
async def generate_animation(req:PromptRequest):
    if validate_prompt(req.prompt):
        try:
            completion = client.chat.completions.create(
                model=os.getenv("MODEL"),
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
                max_tokens=calculate_max_tokens(req.prompt),
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
                return JSONResponse(
                    status_code=500,
                    content=ErrorResponse(
                        err="Manim script generation failed",
                        status_code=500,
                        message="Failed to generate Manim script: No content received."
                    ).model_dump()
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    err="An error occured",
                    status_code=500,
                    message=f"An error occurred during script generation: {str(e)}"
                ).model_dump()
            )
    else:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                err="Invalid prompt",
                status_code=400,
                message="Sorry, this prompt doesn't seem to be related to 2D animations. Please try describing something you want to see visualized, like shapes, movements, or mathematical scenes."
            ).model_dump()
        )
        