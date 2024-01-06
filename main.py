from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ai import Gemini
from typing import List, Literal
from pydantic import BaseModel
import json

app = FastAPI()
gemini = Gemini()

class Content(BaseModel):
    role: Literal["user", "model"]
    parts: List[str]

class ChatHistory(BaseModel):
    content: List[Content]

@app.post("/chat")
async def test(chat_history: ChatHistory):
    try:
        message = chat_history.model_dump()['content']
        response = gemini.chat(message)
        def generate():
            for part in response:
                yield from part.text
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    port = args.p

    uvicorn.run(app, host="127.0.0.1", port=port)
