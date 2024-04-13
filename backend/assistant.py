import asyncio
import typing

from pydantic import BaseModel

import rag_chain


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    content: str


class DocMeta(BaseModel):
    page: int
    source: str


class DocResponse(BaseModel):
    docs: typing.List[DocMeta]


async def fake_answer(message: str) -> typing.AsyncGenerator[str, None]:
    answer = "Minim enim Lorem eiusmod et consectetur voluptate."
    for chunk in [*message.split(), *answer.split()]:
        await asyncio.sleep(0.1)
        yield " " + chunk


class Assistant:
    async def query(self, message: str, use_agent=False):
        stream = await rag_chain.query(message)
        docs = []
        first_ans = ""
        while (chunk := await anext(stream, None)) is not None:
            if "context" in chunk:
                docs.extend(
                    [
                        DocMeta(
                            page=d.metadata["page"],
                            source=d.metadata["source"],
                        )
                        for d in chunk["context"]
                    ]
                )
            elif "answer" in chunk:
                first_ans = chunk["answer"]
                break
            else:
                print(chunk)

        async def answer_stream():
            if first_ans:
                yield first_ans
            while (chunk := await anext(stream, None)) is not None:
                if "answer" in chunk:
                    yield chunk["answer"]

        return docs, answer_stream()

    async def clear_history(self):
        rag_chain.clear_history()
