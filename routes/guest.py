from fastapi import APIRouter,BackgroundTasks,WebSocket,WebSocketDisconnect,status
from fastapi.responses import JSONResponse
from models.error_response import ErrorResponse
from config import client
from pydantic import BaseModel
from services.utils import save_script,render_video,calculate_max_tokens,cleanup_temp_files
from dotenv import load_dotenv
from controllers.cloudinary_uploader import upload_video_to_cloudinary
from controllers.supabase_controller import create_guest_user,delete_guest_user,update_credits
from uuid import uuid4
import os

load_dotenv()

guest_router = APIRouter()

class GuestUserRequest(BaseModel):
    uid:str

class GuestPromptRequest(BaseModel):
    prompt:str
    id:str

active_connections = {}

@guest_router.post('/create_guest')
def create_guest(req:GuestUserRequest):
    try:
        response = create_guest_user(req.uid)
        return {"status":200,"message":"Guest user created","guestData":response}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                err="Something went wrong",
                status_code=500,
                message=str(e)
            ).model_dump()
        )

@guest_router.delete('/delete_guest/{id}')
def delete_guest(id:str):
    try:
        response = delete_guest_user(id)
        return {"status":200,"message":"Guest user deleted","data":response}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                err="Something went wrong",
                status_code=500,
                message=str(e)
            ).model_dump()
        )
    
@guest_router.post('/add_guest_message')
async def add_guest_message(req:GuestPromptRequest,background_tasks: BackgroundTasks = None):
    job_id = str(uuid4())

    background_tasks.add_task(process_guest_animation_job,req,job_id)

    return {"message": "Job started", "job_id": job_id}

async def process_guest_animation_job(req:GuestPromptRequest,job_id:str):
    try:
        await notify_guest_clients(job_id,{
            'status': "started",
            "message": "Generating video based on prompt ..."
        })

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
        script = completion.choices[0].message.content
        if script.startswith("```"):
            script = script.strip("`").strip()
            if script.startswith("python"):
                script = script[len("python"):].strip()
        script_path = save_script(script)
        rendered_video = render_video(script_path.script_path_final,script_path.script_id_final)
        video_url = upload_video_to_cloudinary(rendered_video.video_path,rendered_video.video_id)
        credit_response = update_credits(req.id)

        await notify_guest_clients(job_id, {
            "status": "completed",
            "message": "Video generated successfully.",
            "script": script,
            "video_url": video_url,
            "creditData":credit_response
        })
    except Exception as e:
        await notify_guest_clients(job_id, {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        })
    finally:
        cleanup_temp_files()

@guest_router.websocket('/ws/guest/jobs/{job_id}')
async def websocket_guest_job_updates(websocket:WebSocket,job_id:str):
    try:
        await websocket.accept()

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
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION,reason=str(e))

async def notify_guest_clients(job_id:str,message:dict):
    connections = active_connections.get(job_id,[])

    for ws in connections.copy():
        try:
            await ws.send_json(message)
        except:
            connections.remove(ws)
