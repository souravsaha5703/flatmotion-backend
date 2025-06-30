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
    
    print(user.user.id)
    
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
