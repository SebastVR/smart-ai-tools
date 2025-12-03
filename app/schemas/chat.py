from pydantic import BaseModel


class ChatRequest(BaseModel):
    input: str


class ChatResponse(BaseModel):
    output: str