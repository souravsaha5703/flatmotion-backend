from supabase_config import supabase
from pydantic import BaseModel
from typing import List
from fastapi import Request,HTTPException

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

def insert_chat(chatName: str, message_id: str, userMessage: str, videoScript: str, videoUrl: str, user_id: str):
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

    response = supabase.table("chats").insert(payload).execute()

    return response.data

def get_previous_prompts(chat_id:str):
    existing_messages = supabase.table("chats").select("messages").eq("id",chat_id).single().execute()

    all_messages = existing_messages.data.get("messages",[])

    user_prompts = [msg["userMessage"] for msg in all_messages if "userMessage" in msg]

    return user_prompts

def update_chat(message_id: str, userMessage: str, videoScript: str, videoUrl: str, id: str):

    existing_messages = supabase.table("chats").select("messages").eq("id",id).single().execute()

    all_messages = existing_messages.data.get("messages",[])
    
    messageData = Message(
        id=message_id,
        userMessage=userMessage,
        videoScript=videoScript,
        videoUrl=videoUrl
    )

    updated_messages = all_messages + [messageData.model_dump()]

    updated_response = supabase.table("chats").update({
        "messages": updated_messages
    }).eq("id",id).execute()

    return updated_response.data

def get_all_chats(user_id:str):
    response = supabase.table("chats").select("*").eq("user_id",user_id).execute()

    return response.data

def get_chats(chat_id:str):
    response = supabase.table("chats").select("messages").eq("id",chat_id).execute()

    return response.data