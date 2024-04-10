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
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub

##################
# Define the LLM #
##################

llm = ChatOllama(model="llama2:7b")

#########################
# Define retrieval tool #
#########################

emb = OllamaEmbeddings(model="llama2:7b")

class OllamaEmbeddingFn(chromadb.EmbeddingFunction):
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        return emb.embed_documents(input)
    
# initialise chroma collection
# adapted from https://docs.trychroma.com/usage-guide#using-collections
client = chromadb.PersistentClient(path="documents/chroma_db")
collection = client.get_or_create_collection(
    name="helpsheets", embedding_function=OllamaEmbeddingFn()
)

# paths of documents to index
helpsheet_dir = r"testDocs/helpsheet collection"
helpsheet_paths = [
    f
    for f in os.listdir(helpsheet_dir)
    if os.path.isfile(os.path.join(helpsheet_dir, f))
]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# index documents (takes forever)
# adapted from https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf/#using-pypdf
if collection.count() == 0:
    for i, hs_path in tqdm(enumerate(helpsheet_paths)):
        print(i, hs_path)
        # load document
        loader = PyPDFLoader(os.path.join(helpsheet_dir, hs_path))
        docs = loader.load()
        # split document into chunks
        splits = text_splitter.split_documents(docs)
        # unique ids for each chunk
        ids = [f"{i} - {j}" for j in range(len(splits))]
        # add chunks into chroma collection
        collection.add(
            ids=ids,
            metadatas=[d.metadata for d in splits],
            documents=[d.page_content for d in splits],
        )

# initialise langchain vector store from chroma client
# adapted from https://python.langchain.com/docs/integrations/vectorstores/chroma/#passing-a-chroma-client-into-langchain
vectorstore = Chroma(
    client=client,
    collection_name="helpsheets",
    embedding_function=emb,
)
retriever = vectorstore.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "textbook_search",
    "Only use the tool if the query requires computing theory knowledge on data structures and algorithms.",
)

tools = [retriever_tool]

####################
# Initialise agent #
####################

instructions = """You are an AI computer science tutor for CS2040S data structure and algorithms at National
University of Singapore. you have access to textbook references.
Be concise and ensure output is maximum of 5 sentences.
If you cannot answer the question, do not use any tools, just return "I don't know" as the answer.
"""

base_prompt = hub.pull("langchain-ai/react-agent-template")

print(base_prompt)

prompt = base_prompt.partial(instructions=instructions)

agent = create_react_agent(llm=llm, tools = tools, prompt = prompt)
    
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3, handle_parsing_errors = True)

message_history = ChatMessageHistory()

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

agent_with_chat_history.invoke({"input": "what is a MST"}, {"configurable": {"session_id": "abc123"}})
print(message_history)
print('success')