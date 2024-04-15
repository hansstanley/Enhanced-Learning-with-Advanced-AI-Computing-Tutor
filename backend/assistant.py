import typing

from pydantic import BaseModel

import tutors


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    content: str


class DocMeta(BaseModel):
    page: int
    source: str


class DocResponse(BaseModel):
    docs: typing.List[DocMeta]


class Assistant:
    def __init__(self) -> None:
        # works
        self.tutor = tutors.TutorBase()
        # self.tutor = tutors.TutorWithHistoryRAG(multi_query=True)
        # self.tutor = tutors.TutorWithJsonPrompt(multi_query=True)

        # doesn't work
        # self.tutor = tutors.TutorWithAgent(model="mistral:7b")

    async def query(self, message: str, use_agent=False):
        stream = await self.tutor.query(message)
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
        self.tutor.clear_history()
