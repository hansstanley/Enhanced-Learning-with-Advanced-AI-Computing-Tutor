from typing import AsyncIterable, Iterable

from langchain_community.chat_message_histories.in_memory import (
    ChatMessageHistory,
)
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.messages import AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableGenerator, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory


class TutorBase:
    def __init__(self, model="llama2:7b") -> None:
        self.llm = ChatOllama(model=model)
        self.chain = RunnableWithMessageHistory(
            RunnablePassthrough()
            | ChatPromptTemplate.from_template("{input}")
            | self.llm
            | RunnableGenerator(self._parse_stream, self._aparse_stream),
            get_session_history=lambda _: ChatMessageHistory(),
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    async def query(self, input: str, session_id="abc123"):
        return self.chain.astream(
            {"input": input},
            config={
                "configurable": {"session_id": session_id}
            },  # constructs a key "abc123" in `store`
        )

    def clear_history(self):
        pass

    def _parse_stream(self, chunks: Iterable[AIMessageChunk]):
        for chunk in chunks:
            yield {"answer": chunk.content}

    async def _aparse_stream(self, chunks: AsyncIterable[AIMessageChunk]):
        async for chunk in chunks:
            yield {"answer": chunk.content}
