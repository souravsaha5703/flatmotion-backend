from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from models.prompt import PromptRequest
from models.error_response import ErrorResponse
from config import client
from services.utils import save_script,render_video,calculate_max_tokens,cleanup_temp_files,generate_chat_name
from services.validation import validate_prompt
from dotenv import load_dotenv
from controllers.cloudinary_uploader import upload_video_to_cloudinary
from controllers.supabase_controller import get_current_user_id,insert_chat
from uuid import uuid4
import os

load_dotenv()

router = APIRouter()

@router.post("/generate")
async def generate_animation(req:PromptRequest,user_id:str = Depends(get_current_user_id)):
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
                rendered_video = render_video(script_path.script_path_final,script_path.script_id_final)
                video_url = upload_video_to_cloudinary(rendered_video.video_path,rendered_video.video_id)
                new_message_id = uuid4().hex
                new_chat_name = generate_chat_name(req.prompt)
                try:
                    result = insert_chat(new_chat_name,new_message_id,req.prompt,script,video_url,user_id)
                    return {"message":"chat added","data":result}
                except Exception as e:
                    return JSONResponse(
                        status_code=500,
                        content=ErrorResponse(
                            err="Something went wrong",
                            status_code=500,
                            message=e
                        ).model_dump()
                    )
                finally:
                    cleanup_temp_files()
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
                    message=f"An error occurred during script generation: {e}"
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
        