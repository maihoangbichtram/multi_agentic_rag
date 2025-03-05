# 🔎 Multi Agentic Research (RAG)

- Multi-agentic researcher researches the query/topic from documents fetched from Tavily Search Engine.
- The output is the report about the query/topic based on the retrieved documents.
- The graph ends when the hallucination point is 1, or else the graph restarts from collecting documents from Tavily 
for generated queries to retrieve related info.

## Demo
![img.png](./media/Screenshot%202025-03-05%20at%2016.38.14.png)
![img.png](./media/Screenshot%202025-03-05%20at%2016.38.26.png)
![img.png](./media/Screenshot%202025-03-05%20at%2016.38.57.png)

## Work in progress

1. INTERNAL DOCUMENTATION
2. Access to documents to reliable sources for academic sources (sciencedirect, elsevier, springer, ...)
3. Construct more detail report (e.g Write report for each query)
4. Human input (e.g research plan, sources to fetch documents for queries)

### Installation

1. Install Python 3.11 or later. [Guide](https://www.tutorialsteacher.com/python/install-python).
2. Clone the project and navigate to the directory:

    ```bash
    git clone https://github.com/maihoangbichtram/multi_agentic_rag
    cd multi_agentic_rag
    ```

3. Set up API keys by exporting them or storing them in a `.env` file.

    ```bash
    Copy .env.example to .env
    ```

4. Create a virtual environment

    ```bash
    poetry python3 -m venv .venv
    ```
5. Activate the virtual environment

   ```bash
   . .venv/bin/activate
   ```
5. Install dependencies and start the server:

    ```bash
    pip install -r requirements.txt
    ```
6. Start the application

   ```bash
    python app.py
    ```
