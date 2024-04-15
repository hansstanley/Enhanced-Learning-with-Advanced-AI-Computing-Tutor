import os

import chromadb
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.tools.retriever import create_retriever_tool
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

DB_PATH = "documents/docs_db"
COLLECTION_NAME = "helpsheets"
COLLECTION_DESC = """Provides very useful helpsheets with \
computing theory knowledge on data structures and algorithms."""
RETRIEVER_MODEL = "llama2:7b"

llm = ChatOllama(model=RETRIEVER_MODEL)
emb = OllamaEmbeddings(model=RETRIEVER_MODEL)


class OllamaEmbeddingFn(chromadb.EmbeddingFunction):
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        return emb.embed_documents(input)


# initialise chroma client
client = chromadb.PersistentClient(path=DB_PATH)


def index_docs_from_dir(dir_path: str, reset=False):
    # adapted from https://docs.trychroma.com/usage-guide#using-collections
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=OllamaEmbeddingFn()
    )
    if collection.count() > 0:
        if reset:
            client.delete_collection(COLLECTION_NAME)
            collection = client.create_collection(
                name=COLLECTION_NAME, embedding_function=OllamaEmbeddingFn()
            )
        else:
            return
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    fps = [
        fp
        for fp in os.listdir(dir_path)
        if os.path.isfile(
            os.path.join(dir_path, fp),
        )
    ]
    fps_tqdm = tqdm(enumerate(fps))
    for i, fp in fps_tqdm:
        fps_tqdm.set_description(f"{i}: {fp}")
        # load document
        loader = PyPDFLoader(os.path.join(dir_path, fp))
        docs = loader.load()
        # split document into chunks
        splits = splitter.split_documents(docs)
        # unique ids for each chunk
        ids = [f"{i} - {j}" for j in range(len(splits))]
        # add chunks into chroma collection
        collection.add(
            ids=ids,
            metadatas=[d.metadata for d in splits],
            documents=[d.page_content for d in splits],
        )


def get_vectorstore():
    # initialise langchain vector store from chroma client
    return Chroma(
        client=client,
        collection_name="helpsheets",
        embedding_function=emb,
    )


def get_retriever(multi_query=True, compress=True):
    retriever = get_vectorstore().as_retriever(
        search_type="mmr", search_kwargs={"k": 3}
    )

    if multi_query:
        # multi query retriever adapted from
        # https://python.langchain.com/docs/modules/data_connection/retrievers/MultiQueryRetriever/
        retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=llm,
            include_original=True,
        )

    if compress:
        # contextual compression adapted from
        # https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression/
        # compressor = LLMChainExtractor.from_llm(llm)
        compressor = LLMChainFilter.from_llm(llm)
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=retriever,
        )

    return retriever


def get_retriever_tool(multi_query=True, compress=True):
    return create_retriever_tool(
        get_retriever(multi_query=multi_query, compress=compress),
        COLLECTION_NAME,
        COLLECTION_DESC,
    )


if __name__ == "__main__":
    reset_ans = input("Reset index? [y/N]: ")
    reset = reset_ans.strip().lower() == "y"
    # takes a long time
    index_docs_from_dir(
        r"frontend/src/documents/training_set",
        reset=reset,
    )
