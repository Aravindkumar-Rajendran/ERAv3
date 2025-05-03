import streamlit as st
import random
import time
import asyncio
import chromadb
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.core.agent.workflow import AgentWorkflow


Settings.verbose_logging = True


# initialize client
db = chromadb.PersistentClient(path="./chroma_db")

# get collection
chroma_collection = db.get_or_create_collection("erav3")

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434",
    request_timeout=360.0)

llm = Ollama(model="llama3.1:8b", request_timeout=360.0)

index = VectorStoreIndex.from_vector_store(
    vector_store, 
    storage_context=storage_context,
    embed_model=embed_model,
)
query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)
retriever = index.as_retriever(similarity_top_k=3)

# define tools
def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


async def search_documents(query: str) -> str:
    """Useful for searching through documents."""
    print("\n"+"-" * 20)
    print("Search Tool")
    print("-" * 20)
    print(f"Query: {query}")
    results = retriever.retrieve(query)
    file_url = f"file:///{str(results[0].node.metadata['file_path']).replace(' ', '%20')}#page={results[0].node.metadata['page_label']}"
    response = "Matching document:" + str(results[0].node.get_content()) + "\n" + "Citations: " + file_url 
    print(f"Response: {response}")
    return response


async def query_documents(query: str) -> str:
    """Useful for answering natural language questions."""
    print("\n"+"-" * 20)
    print("Search Tool")
    print("-" * 20)
    print(f"Query: {query}")
    response = await query_engine.aquery(query)
    print(f"Response: {response}")
    return str(response)

# Create an enhanced workflow with both tools
agent = AgentWorkflow.from_tools_or_functions(
            [multiply, search_documents],
            llm=llm,
            system_prompt="""You are a helpful assistant that can perform calculations
            and search through documents to answer questions. Provide direct answers from the search tools as response.
            Add the same citations that you get in the end of search_documents tool response STRICTLY.
            """,
)


# Streamed response emulator
async def response_generator(prompt):
    print("\n"+"-" * 20)
    print("Agent")
    print("-" * 20)
    print(f"Prompt: {prompt}")
    response = await agent.run(prompt)
    print("\n"+"-" * 20)
    print("Agent Response")
    print(f"Response: {response}")
    return response

st.title("ERAI Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

async def main():
    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = await response_generator(prompt)
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Run the agent
if __name__ == "__main__":
    asyncio.run(main())