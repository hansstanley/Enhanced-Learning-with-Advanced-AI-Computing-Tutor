import os
import chromadb
from tqdm import tqdm
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub
import helpsheet_retriever

##################
# Define the LLM #
##################

# mistral seems to perform better than llama2
# in following agent instructions
llm = ChatOllama(model="mistral:7b")

#########################
# Define retrieval tool #
#########################

tools = [helpsheet_retriever.get_retriever_tool()]

####################
# Initialise agent #
####################

instructions = """You are an AI computer science tutor for \
CS2040S data structures and algorithms at \
National University of Singapore. \
You make sure that knowledge questions are answered accurately \
according to the given tools.
Be concise and ensure output is maximum of 5 sentences.
If you cannot answer the question, even after using tools, \
just return "I don't know" as the answer.
"""

# base_prompt = hub.pull("hwchase17/react")
base_prompt = hub.pull("langchain-ai/react-agent-template")

prompt = base_prompt.partial(instructions=instructions)
print(prompt.template)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5, handle_parsing_errors = True)

message_history = ChatMessageHistory()

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

while True:
    query = input("\nQuery: ").strip()
    if not query:
        break
    answer = agent_with_chat_history.invoke(
        {"input": query},
        {"configurable": {"session_id": "abc123"}},
    )
    print("Answer:", answer)
# print(message_history)
