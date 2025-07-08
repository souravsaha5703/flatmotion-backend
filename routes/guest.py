from fastapi import APIRouter,WebSocket,WebSocketDisconnect,status
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

@guest_router.websocket('/ws/guest/jobs')
async def websocket_guest_job_updates(websocket:WebSocket):
    try:
        await websocket.accept()

        data = await websocket.receive_json()
        prompt = data.get("prompt")
        guest_id = data.get("guest_id")
        job_id = str(uuid4())

        if not prompt or not guest_id:
            await websocket.send_json({"status": "error", "message": "Prompt and guest_id required"})
            await websocket.close()
            return
        
        if job_id not in active_connections:
            active_connections[job_id] = []
        active_connections[job_id].append(websocket)

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
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=calculate_max_tokens(prompt),
            )
            script = completion.choices[0].message.content
            if script.startswith("```"):
                script = script.strip("`").strip()
                if script.startswith("python"):
                    script = script[len("python"):].strip()
            script_path = save_script(script)
            rendered_video = render_video(script_path.script_path_final,script_path.script_id_final)
            video_url = upload_video_to_cloudinary(rendered_video.video_path,rendered_video.video_id)
            credit_response = update_credits(guest_id)

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
                "message": "Error occured in generating video"
            })
        finally:
            cleanup_temp_files()

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            active_connections[job_id].remove(websocket)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))

async def notify_guest_clients(job_id:str,message:dict):
    connections = active_connections.get(job_id,[])

    for ws in connections.copy():
        try:
            await ws.send_json(message)
        except:
            connections.remove(ws)
