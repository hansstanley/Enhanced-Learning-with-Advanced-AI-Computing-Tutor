import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.assistant import Assistant, ChatRequest, ChatResponse, DocResponse

app = FastAPI()
assistant = Assistant()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "Hello World!"


@app.post("/chat")
async def chat(body: ChatRequest):
    docs, answer_stream = await assistant.query(body.query)

    async def streamer():
        yield DocResponse(docs=docs).model_dump_json() + "\n"
        await asyncio.sleep(0.1)
        async for chunk in answer_stream:
            yield ChatResponse(content=chunk).model_dump_json() + "\n"

    return StreamingResponse(streamer(), media_type="application/json")


@app.post("/chat/clear")
async def clear_history():
    await assistant.clear_history()
    return None
