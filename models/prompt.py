from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    prompt_res: str

class ModificationRequest(BaseModel):
    prompt: str
    chat_id: str