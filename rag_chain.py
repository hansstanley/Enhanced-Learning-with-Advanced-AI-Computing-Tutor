import json
from typing import Any, List, Literal

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain.chains.retrieval import create_retrieval_chain
from langchain.globals import set_debug
from langchain_community.chat_message_histories.in_memory import (
    ChatMessageHistory,
)
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    get_buffer_string,
)
from langchain_core.prompt_values import ChatPromptValue, PromptValue
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

import helpsheet_retriever

set_debug(True)


class StudentMessage(HumanMessage):
    type: Literal["student"] = "student"


class TutorMessage(AIMessage):
    type: Literal["tutor"] = "tutor"


class CustomPromptValue(ChatPromptValue):
    ai_prefix = "Tutor"
    human_prefix = "Student"

    def to_string(self) -> str:
        print("BOOM CustomPromptValue to_string")
        return get_buffer_string(
            self.messages,
            ai_prefix=self.ai_prefix,
            human_prefix=self.human_prefix,
        )


class CustomPromptTemplate(ChatPromptTemplate):
    def format_prompt(self, **kwargs: Any) -> PromptValue:
        return CustomPromptValue(messages=self.format_messages(**kwargs))

    async def aformat_prompt(self, **kwargs: Any) -> PromptValue:
        return CustomPromptValue(
            messages=await self.aformat_messages(**kwargs),
        )


class CustomHistory(ChatMessageHistory):
    ai_prefix = "Tutor"
    human_prefix = "Student"

    def __str__(self) -> str:
        print("BOOM custom history __str__")
        return get_buffer_string(
            self.messages,
            ai_prefix=self.ai_prefix,
            human_prefix=self.human_prefix,
        )


def convert_message(message: BaseMessage):
    print("BOOM converting message", type(message), message)
    if isinstance(message, HumanMessage):
        return StudentMessage(content=message.content)
    if isinstance(message, AIMessage):
        return TutorMessage(content=message.content)
    else:
        return message


class CustomMessagesPlaceholder(MessagesPlaceholder):
    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        print("BOOM CustomMessagesPlaceholder format_messages")
        messages = super().format_messages(**kwargs)
        return list(map(convert_message, messages))

    def __add__(self, other: Any) -> ChatPromptTemplate:
        prompt = CustomPromptTemplate(
            messages=[self],
        )  # type: ignore[call-arg]
        return prompt + other


llm = ChatOllama(model="llama2:7b")

retriever = helpsheet_retriever.get_retriever(
    compress=False,
    multi_query=False,
)

# Contextualize question
contextualize_q_system_prompt = """Given a chat history and \
the latest user question which might reference context in the chat history, \
formulate a standalone question which can be understood \
without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_system_prompt = """Computing Concepts to be considered: ###
{context}
###

[INSTRUCTIONS] Your AI role description JSON as the Computer Science tutor \
at the National University of Singapore is given below, \
ensure your output is with reference to your role description as stated below:
###
{instructions}
###

Reminder, you are the Computer Science Tutor at \
National University of Singapore, ensure your output is with reference to \
content provided and your role description json above. 

Refresh on the content and  "AI Role Description" JSON. \
If you have understood your AI role description as \
the Computer Science Tutor at National University of Singapore, \
continue the conversation below. Do not break character and \
check your output against the provided AI role description. \
Ensure your output fits in well with conversation history below.
"""
# qa_system_prompt = """You are an computer science tutor \
# for question-answering tasks. \
# For questions about definition, be as concise as possible. \
# For problem-solving questions, answer in the format: ###
# Hint:
# (list of hints)
# Possible Solution:
# (solution) ###
# DO NOT answer any questions in the context. \
# You may use your own knowledge as well, but you need to state clearly \
# which part is from your own knowledge. Do not mention "the context". \
# If you don't know the answer or the question is NOT RELEVANT to \
# Data Structure or Algorithms, just say this single sentence \
# "Hmm, this problem seems to be out of syllabus. \
# Please further check with your tutor." Refrain from making up an answer. \

# Context: ###
# {context} ###"""
qa_prompt = CustomPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        CustomMessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

with open("instructions.json") as f:
    d = json.load(f)
    qa_prompt = qa_prompt.partial(instructions=d)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(
    history_aware_retriever,
    question_answer_chain,
)

store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = CustomHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


async def query(input: str, session_id="abc123"):
    return conversational_rag_chain.astream(
        {"input": input},
        config={
            "configurable": {"session_id": session_id}
        },  # constructs a key "abc123" in `store`.
    )


def clear_history():
    store.clear()
