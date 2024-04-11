import asyncio
import typing

from pydantic import BaseModel


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
    async def query(self, message: str):  # TODO
        return [
            DocMeta(
                page=2,
                source="documents/LN/02.Java-OOP.pdf",
            ),
            DocMeta(
                page=3,
                source="documents/LN/06.SortingB.pdf",
            ),
        ], fake_answer(message)

    async def clear_history(self):  # TODO
        pass
