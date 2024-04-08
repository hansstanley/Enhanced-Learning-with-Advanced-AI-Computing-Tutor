import langchain
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("example_data/layout-parser-paper.pdf")
pages = loader.load_and_split()


llm = Ollama(model="llama2")
