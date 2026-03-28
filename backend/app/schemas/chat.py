from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    message: str


class AddMessageRequest(BaseModel):
    message: str
