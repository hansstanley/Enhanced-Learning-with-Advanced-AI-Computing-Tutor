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
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.tools.retriever import create_retriever_tool

llm = ChatOllama(model="llama2:7b")
emb = OllamaEmbeddings(model="llama2:7b")

# Define retrieval tool
retriever
retriever_tool = create_retriever_tool(
    retriever,
    "textbook_search",
    "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
)