from researcher_graph.graph_states import ResearcherState, QueryState
from researcher_graph.researcher import ResearchConductor
from typing import cast
from utils.prompt import GENERATE_QUERIES_SYSTEM_PROMPT
from utils.utils import config

from dotenv import load_dotenv
import logging

from langchain_cohere import CohereRerank
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_2_0_FLASH = config['llm']['gemini_2_0_flash']
TEMPERATURE = config['llm']['temperature']
TOP_K = config['retriever']['top_k']
ENSEMBLE_WEIGHTS = config['retriever']['ensemble_weights']
TOP_K_COMPRESSION = config['retriever']['top_k_compression']
COHERE_RERANK_MODEL = config['retriever']['cohere_rerank_model']

async def _load_documents(query):
    research_conductor = ResearchConductor()
    documents = await research_conductor.conduct_research(query)
    return documents

def _build_retrievers(documents: list[Document]):
    retriever_bm25 = BM25Retriever.from_documents(documents, search_kwargs={"k": TOP_K})
    #retriever_vanilla = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": TOP_K})
    #retriever_mmr = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": TOP_K})

    ensemble_retriever = EnsembleRetriever(
        #retrievers=[retriever_vanilla, retriever_mmr, retriever_bm25],
        retrievers=[retriever_bm25],
        weights=ENSEMBLE_WEIGHTS,
    )

    compressor = CohereRerank(top_n=TOP_K_COMPRESSION, model=COHERE_RERANK_MODEL)

    # Build compression retriever
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever,
    )

    return compression_retriever


async def generate_queries(state: ResearcherState, *, config: RunnableConfig):
    class Response(BaseModel):
        queries: list[str] = Field(description="list of generated search queries")

    logger.info("---GENERATE QUERIES---")
    logger.info(f"Quesion: {state.question}")
    model = ChatGoogleGenerativeAI(model=GEMINI_2_0_FLASH, temperature=TEMPERATURE)
    messages = [
        {"role": "system", "content": GENERATE_QUERIES_SYSTEM_PROMPT},
        {"role": "user", "content": state.question}
    ]

    response = cast(Response, await model.with_structured_output(Response).ainvoke(messages))
    logger.info(f"Queries: {response.queries}")
    return {"queries": response.queries}

def retrieve_in_parallel(state: ResearcherState, *, config: RunnableConfig):
    return [
        Send("retrieve_and_rerank_documents", QueryState(query=query)) for query in state.queries
    ]

async def retrieve_and_rerank_documents(state: QueryState, *, config: RunnableConfig):
    logger.info("---RETRIEVE DOCUMENTS---")
    logger.info(f"Query for the retrieval process: {state.query}")

    documents = await _load_documents(state.query)

    if len(documents) == 0:
        return {"documents": []}
    composer_retriever = _build_retrievers(documents)

    response = composer_retriever.invoke(state.query)
    return {"documents": response}


graph_builder = StateGraph(ResearcherState)
graph_builder.add_node(generate_queries)
graph_builder.add_node(retrieve_and_rerank_documents)
graph_builder.add_edge(START, "generate_queries")
graph_builder.add_conditional_edges(
    "generate_queries",
    retrieve_in_parallel,
    path_map=["retrieve_and_rerank_documents"]
)
graph_builder.add_edge("retrieve_and_rerank_documents", END)
research_graph = graph_builder.compile()
