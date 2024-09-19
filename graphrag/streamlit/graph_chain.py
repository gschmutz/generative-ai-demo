from json import loads, dumps

from langchain_community.vectorstores import Neo4jVector
from langchain.chains import RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferMemory

# Lancgchain for Ollama (for hosting a local LLM)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama

from langchain_community.graphs import Neo4jGraph

# Use Langchain Hub (to get prompts)
from langchain import hub

from neo4j import GraphDatabase
from dotenv import load_dotenv

#from retry import retry
import os
import textwrap
import logging
import streamlit as st

load_dotenv()  # take environment variables from .env.

# Load from environment
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'

# Global constants
VECTOR_INDEX_NAME = 'chunks_vector'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'embedding'

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_API = os.getenv('EMBEDDING_API') or 'openai'
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL') or 'text-embedding-ada-002'
CHAT_API = os.getenv('CHAT_API') or 'openai'
CHAT_MODEL = os.getenv('CHAT_MODEL') or 'gpt-3.5-turbo'
OLLAMA_URL = os.getenv('OLLAMA_URL')

print ("OLLAMA_URL: " + OLLAMA_URL )

embeddings_api = OllamaEmbeddings(base_url=OLLAMA_URL, model=EMBEDDING_MODEL, temperature=0, top_k=10, top_p=0.5)
chat_api = ChatOllama(base_url=OLLAMA_URL, model=CHAT_MODEL, temperature=0)

gdb = GraphDatabase.driver(uri=NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
graph = Neo4jGraph()

MEMORY = ConversationBufferMemory(
    memory_key="chat_history",
    input_key="question",
    output_key="answer",
    return_messages=True,
)

# helper function to pretty print the chain's response
def prettifyChain(chain):
  def prettychain(question:str):
    response = chain({"question": question, "query":question}, return_only_outputs=True,)
    answer = response['answer'] if ('answer' in response) else response['result']
    print(textwrap.fill(answer, 80))
  return prettychain

retrieval_query_parent = """

    WITH node AS chunk, score AS score ORDER BY score 
    OPTIONAL MATCH (chunk:Chunk)<-[:CONTAINS]-(parent)
    OPTIONAL MATCH (parent)-[:CONTAINS]->(s:Chunk)
    WITH chunk, s, score ORDER BY s.chunkSeqId ASC
    WITH collect(s.text) as textList, chunk.text as text, score AS score
    RETURN apoc.text.join(textList, " \n ")  as text,
    score,  {} AS metadata 
    ORDER BY score desc

"""

index_name = "chunks_vector"
vector_store = None

def init_vector_chain(retrieval_query):

    try:
        logging.debug(f"Attempting to retrieve existing vector index: {index_name}...")
        vector_store = Neo4jVector.from_existing_index(
            embedding=embeddings_api,
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name=index_name,
            embedding_node_property='embedding',
            retrieval_query=retrieval_query
        )
        logging.debug(f"Using existing index: {index_name}")
    except:
        logging.debug(
            f"No existing index found. Attempting to create a new vector index named {index_name}..."
        )
        try:
            vector_store = Neo4jVector.from_existing_graph(
                embedding=embeddings_api,
                url=NEO4J_URI,
                username=NEO4J_USERNAME,
                password=NEO4J_PASSWORD,
                index_name=index_name,
                node_label="Chunk",
                text_node_properties=["text"],
                embedding_node_property='embedding',
                retrieval_query=retrieval_query
            )
            logging.debug(f"Created new index: {index_name}")
        except Exception as e:
            logging.error(f"Failed to retrieve existing or to create a Neo4jVector: {e}")

    if vector_store is None:
        logging.error(f"Failed to retrieve or create a Neo4jVector. Exiting.")
        exit()

    # RAG prompt
    prompt = hub.pull("rlm/rag-prompt-llama")

    vector_retriever = vector_store.as_retriever()

    vector_chain = RetrievalQA.from_chain_type(
        chat_api, 
        chain_type="stuff", 
        retriever=vector_retriever, 
    #    memory=MEMORY,
        verbose=True, 
        chain_type_kwargs={"prompt": prompt, "verbose": True}
    )
    return vector_chain

def get_results(question, strategy) -> str:
    """Generate response using Neo4jVector using vector index only

    Args:
        question (str): User query

    Returns:
        str: Formatted string answer with citations, if available.
    """

    logging.info(f"Using Neo4j url: {NEO4J_URI}")
    print(">>>>>>>>>>>> strategy:")
    print(strategy)
    
    retrieval_query = None
    if (strategy == "Tradional RAG"):
        None
    elif (strategy == "Parent Retriever RAG"):
        retrieval_query = retrieval_query_parent
    vector_chain = init_vector_chain(retrieval_query)

    # Returns a dict with keys: answer, sources
    chain_result = vector_chain.invoke(
        {"query": question},
#        prompt=prompt,
        return_only_outputs=True,
    )

    logging.debug(f"chain_result: {chain_result}")
    
    result = chain_result

    # Cite sources, if any
    #sources = chain_result["sources"]
    #sources_split = sources.split(", ")
    #for source in sources_split:
    #    if source != "" and source != "N/A" and source != "None":
    #        result += f"\n - [{source}]({source})"

    return result


