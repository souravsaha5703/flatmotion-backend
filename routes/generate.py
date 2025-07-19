from fastapi import APIRouter,Depends,BackgroundTasks,WebSocket,WebSocketDisconnect,status
from fastapi.responses import JSONResponse
from models.prompt import PromptRequest,ModificationRequest
from models.error_response import ErrorResponse
from config import client
from services.utils import save_script,render_video,calculate_max_tokens,cleanup_temp_files,generate_chat_name
from services.validation import validate_prompt
from dotenv import load_dotenv
from controllers.cloudinary_uploader import upload_video_to_cloudinary
from controllers.supabase_controller import get_current_user_id,insert_chat,get_previous_prompts,update_chat,get_messages,get_all_chats,get_current_user_id_ws
from uuid import uuid4
import os

load_dotenv()

router = APIRouter()

active_connections = {}

@router.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok", "message": "Flatmotion Backend is healthy!"}

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
                    result = await insert_chat(new_chat_name,new_message_id,req.prompt,script,video_url,user_id)
                    return {"message":"Chat added successfully","data":result}
                except Exception as e:
                    return JSONResponse(
                        status_code=500,
                        content=ErrorResponse(
                            err="Something went wrong",
                            status_code=500,
                            message=str(e)
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
        
@router.put('/add_message')
async def add_message(req:ModificationRequest,user_id:str = Depends(get_current_user_id),background_tasks: BackgroundTasks = None):
    job_id = str(uuid4())

    background_tasks.add_task(process_animation_job,req,user_id,job_id)

    return {"message": "Job started", "job_id": job_id}

async def process_animation_job(req:ModificationRequest,user_id:str,job_id:str):
    try:
        await notify_clients(job_id,{
            'status': "started",
            "message": "Generating video based on prompt ..."
        })

        previous_prompts = await get_previous_prompts(req.chat_id)

        completion = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": os.getenv("MODIFICATION_CONTENT")
                },
                {
                    "role": "user",
                    "content": (
                    f"Previous animation prompt:\n{previous_prompts}\n\n"
                    f"Modified prompt:\n{req.prompt}"
                )
                }
            ],
            temperature=0.7,
            max_tokens=calculate_max_tokens(req.prompt),
        )
        script = completion.choices[0].message.content
        if script.startswith("```"):
            script = script.strip("`").strip()
            if script.startswith("python"):
                script = script[len("python"):].strip()
        script_path = save_script(script)
        rendered_video = render_video(script_path.script_path_final,script_path.script_id_final)
        video_url = upload_video_to_cloudinary(rendered_video.video_path,rendered_video.video_id)
        new_message_id = uuid4().hex
        result = await update_chat(new_message_id, req.prompt, script, video_url, req.chat_id)

        await notify_clients(job_id, {
            "status": "completed",
            "message": "Video generated successfully.",
            "script": script,
            "video_url": video_url,
            "chat_update": result
        })
    except Exception as e:
        await notify_clients(job_id, {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        })
    finally:
        cleanup_temp_files()

@router.websocket('/ws/jobs/{job_id}')
async def websocket_job_updates(websocket:WebSocket,job_id:str):
    try:
        user_id = await get_current_user_id_ws(websocket)
        await websocket.accept()
        print(user_id)

        if job_id not in active_connections:
            active_connections[job_id] = []
        active_connections[job_id].append(websocket)

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            active_connections[job_id].remove(websocket)
    except Exception as e:
        print(f"WebSocket auth failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason="Auth failed: Token expired")

async def notify_clients(job_id:str,message:dict):
    connections = active_connections.get(job_id,[])

    for ws in connections.copy():
        try:
            await ws.send_json(message)
        except:
            connections.remove(ws)

@router.get("/get_messages/{chatId}")
async def get_all_messages(chatId:str,user_id:str = Depends(get_current_user_id)):
    try:
        result = await get_messages(chatId)
        return {"message":"Chats fetched successfully","data":result}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                err="Error in getting messages",
                status_code=400,
                message=str(e)
            ).model_dump()
        )
    
@router.get("/get_all_chats")
async def get_chats(user_id:str = Depends(get_current_user_id)):
    try:
        result = await get_all_chats(user_id)
        return {"message":"All chats fetched successfully","chats":result}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                err="Error in getting messages",
                status_code=400,
                message=str(e)
            ).model_dump()
        )