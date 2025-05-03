# ERAI v0 - AI Assistant for learning AI

Agentic RAG for Learning AI built using LlamaIndex and Ollama for answering questions about AI with ERAv3 course content as context.

Models used:  
**Agent**: llama3.1:8b  
**Embeddings**: nomic-text-embed  

Tools:
- **Search_tool**: Retrieve context from LlamaIndex
- **Multiply**: sample math tool 

We can add more tools, for simplicity and checking RAG workflow, I hae just used above two tools. 

### Installation

```uv venv .venv```

`activate .venv`

```uv pip install -r requirements.txt```

### Run

1. Get the index - ChromaDB (not in git)
2. `uv run streamlit run streamlit_app.py`










### Assignment details:

Build a Chrome plugin that:

For every web page that you visit (skip confidential ones like Gmail, WhatsApp, etc), builds a nomic embedding (or any other model that you can run) and then builds an FAISS index with URL
Please remember that you only need the index file, so you can do it on Google Colab and then download this index file as well
When you search within your plugin, it opens the website where that content is and highlights it as well!
1000 Pts for above

OR

2000 Pts total if you come up with an amazing idea to use RAG (locally or on browser). 
Share your YouTube Video and GitHub link.