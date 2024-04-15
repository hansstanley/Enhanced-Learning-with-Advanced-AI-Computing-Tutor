import json
from typing import AsyncIterable, Iterable

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain.chains.retrieval import create_retrieval_chain
from langchain.globals import set_debug
from langchain.tools.retriever import create_retriever_tool
from langchain_community.chat_message_histories.in_memory import (
    ChatMessageHistory,
)
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessageChunk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableGenerator, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

import helpsheet_retriever

set_debug(True)

DEFAULT_SYSTEM_PROMPT = """You are a Computer Science tutor \
for question-answering tasks.
For questions about definition and concept, \
be as concise as possible and answer in at most 5 sentences.
You may use your own knowledge, but state clearly when you do.
Do NOT mention "the context".
Do NOT answer questions in the context.
If you cannot answer, do not know the answer, or think \
the questions is irrelevant to data structures or algoritms, \
state clearly and say "Please check with your tutor." \
Refrain from making up an answer."""

DEFAULT_QUESTION_PROMPT = """You are given chat history and \
the latest user question which might reference the chat history. \
If needed, formulate a standalone question that captures both \
the chat history and the question. \
Otherwise, return the question as is. \
Refrain from answering the question."""


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


class TutorWithHistoryRAG(TutorBase):
    def __init__(
        self,
        model="llama2:7b",
        multi_query=False,
        compress=False,
        qa_prompt: ChatPromptTemplate | None = None,
    ) -> None:
        self.llm = ChatOllama(model=model)
        self.store = {}

        retriever = helpsheet_retriever.get_retriever(
            multi_query=multi_query,
            compress=compress,
        )

        # Contextualize question
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", DEFAULT_QUESTION_PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )

        qa_system_prompt = "\n".join(
            [
                DEFAULT_SYSTEM_PROMPT,
                "Context: ###",
                "{context}",
                "###",
            ]
        )
        qa_prompt = qa_prompt or ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(
            self.llm,
            qa_prompt,
        )
        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain,
        )

        self.chain = RunnableWithMessageHistory(
            rag_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    def clear_history(self):
        self.store.clear()

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]


class TutorWithJsonPrompt(TutorWithHistoryRAG):
    def __init__(
        self,
        model="llama2:7b",
        multi_query=False,
        compress=False,
    ) -> None:
        qa_system_prompt = """Content and concepts to be considered: ###
        {context}
        ###

        Your AI role description JSON as the Computer Science tutor \
        at the National University of Singapore is given below, \
        ensure your output is with reference to your role description: ###
        {instructions}
        ###

        Refresh on the content and "AI Role Description" JSON from above. \
        If you have understood your AI role description as \
        the Computer Science Tutor at National University of Singapore, \
        continue the conversation below. Do not break character and \
        check your output against the provided AI role description. \
        Ensure your output fits in well with conversation history below.
        """
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        with open("instructions.json") as f:
            qa_prompt = qa_prompt.partial(instructions=json.load(f))

        super().__init__(model, multi_query, compress, qa_prompt)


class CustomReActOutputParser(ReActSingleInputOutputParser):
    def parse(self, text: str) -> AgentAction | AgentFinish:
        res = super().parse(text)
        if isinstance(res, AgentFinish):
            return AgentFinish(
                {"action": res.return_values["output"]},
                res.log,
            )
        return res


class TutorWithAgent(TutorBase):
    def __init__(
        self,
        model="llama2:7b",
        multi_query=False,
        compress=False,
    ) -> None:
        self.llm = ChatOllama(model=model)
        self.store = {}

        retriever = helpsheet_retriever.get_retriever(
            multi_query=multi_query,
            compress=compress,
        )

        # Contextualize question
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", DEFAULT_QUESTION_PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )
        retriever_tool = create_retriever_tool(
            history_aware_retriever,  # type: ignore
            name=helpsheet_retriever.COLLECTION_NAME,
            description=helpsheet_retriever.COLLECTION_DESC,
        )

        prompt = hub.pull("langchain-ai/react-agent-template")
        prompt = prompt.partial(instructions=DEFAULT_SYSTEM_PROMPT)

        agent = create_react_agent(
            llm=self.llm,
            tools=[retriever_tool],
            prompt=prompt,
            output_parser=CustomReActOutputParser(),
        )
        agent_executor = AgentExecutor(
            agent=agent,  # type: ignore
            tools=[retriever_tool],
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )

        self.chain = RunnableWithMessageHistory(
            RunnablePassthrough() | agent_executor | StrOutputParser(),
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            # output_messages_key="answer",
        )

    def clear_history(self):
        self.store.clear()

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
