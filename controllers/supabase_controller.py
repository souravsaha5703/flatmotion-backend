from supabase_config import supabase
from pydantic import BaseModel
from typing import List
from fastapi import Request,HTTPException,WebSocket,status
import asyncio

class Message(BaseModel):
    id: str
    userMessage: str
    videoScript: str
    videoUrl: str

class Chat(BaseModel):
    chatName:str
    messages: List[Message]

async def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    refresh_token = request.headers.get("x-refresh-token")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    access_token = auth_header.split(" ")[1]

    supabase.auth.set_session(access_token=access_token, refresh_token=refresh_token or "")

    user = supabase.auth.get_user()
    if not user or not user.user:
        raise HTTPException(status_code=403, detail="Invalid or expired user session")
    
    return user.user.id 

async def get_current_user_id_ws(websocket: WebSocket) -> str:
    token = websocket.query_params.get("token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token in WebSocket")

    user = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired WebSocket session")
    
    return user.user.id
 
async def insert_chat(chatName: str, message_id: str, userMessage: str, videoScript: str, videoUrl: str, user_id: str):
    messageData = Message(
        id=message_id,
        userMessage=userMessage,
        videoScript=videoScript,
        videoUrl=videoUrl
    )

    payload = {
        "chatName": chatName,
        "user_id": user_id,
        "messages": [messageData.model_dump()]
    }

    return await asyncio.to_thread(
        lambda: supabase.table("chats").insert(payload).execute().data
    )

async def get_previous_prompts(chat_id:str):
    existing_messages = await asyncio.to_thread(
        lambda: supabase.table("chats").select("messages").eq("id",chat_id).single().execute()
    )

    all_messages = existing_messages.data.get("messages",[])

    user_prompts = [msg["userMessage"] for msg in all_messages if "userMessage" in msg]

    return user_prompts

async def update_chat(message_id: str, userMessage: str, videoScript: str, videoUrl: str, id: str):

    existing_messages = await asyncio.to_thread(
        lambda: supabase.table("chats").select("messages").eq("id",id).single().execute()
    )

    all_messages = existing_messages.data.get("messages",[])
    
    messageData = Message(
        id=message_id,
        userMessage=userMessage,
        videoScript=videoScript,
        videoUrl=videoUrl
    )

    updated_messages = all_messages + [messageData.model_dump()]

    updated_response = await asyncio.to_thread(
        lambda: supabase.table("chats").update({"messages": updated_messages}).eq("id",id).execute()
    )

    return updated_response.data

async def get_all_chats(user_id:str):
    response = await asyncio.to_thread(
        lambda: supabase.table("chats").select("*").eq("user_id",user_id).execute()
    )

    return response.data

async def get_messages(chat_id:str):
    response = await asyncio.to_thread(
        lambda: supabase.table("chats").select("messages").eq("id",chat_id).execute()
    )

    return response.data

def create_guest_user(guest_uid:str):
    payload = {
        "guest_uid":guest_uid,
        "credits":5,
        "is_guest":True
    }

    return supabase.table("guest_credits").insert(payload).execute().data

def delete_guest_user(id:str):
    response = supabase.table("guest_credits").delete().eq('id',id).execute()

    return response.data

def update_credits(id:str):
    guest_data = supabase.table("guest_credits").select("credits").eq("id",id).single().execute()

    if not guest_data.data:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    credits = guest_data.data["credits"]
    if credits <= 0:
        raise HTTPException(status_code=403, detail="No credits left. Please sign up to continue.")
    
    updated = supabase.table("guest_credits").update({"credits": credits - 1}).eq("id", id).execute()

    if updated.error:
        raise HTTPException(status_code=500, detail="Failed to update credits")
    
    return updated.data