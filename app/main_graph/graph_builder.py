from app.main_graph.graph_states import AgentState, InputState, HalluciantionGrade
from app.researcher_graph.graph_builder import research_graph
from app.utils.prompt import RESEARCH_PLAN_SYSTEM_PROMPT, RESPONSE_SYSTEM_PROMPT, CHECK_HALLUCINATIONS
from app.utils.utils import config

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv
import logging
from typing import TypedDict, cast, List, Optional

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logging.getLogger("openai").propagate = False
logging.getLogger("google_genai").propagate = False
logging.getLogger("urllib3").propagate = False
logging.getLogger("httpx").propagate = False

GEMINI_2_0_FLASH = config['llm']['gemini_2_0_flash']
GEMINI_2_0_PRO = config['llm']['gemini_2_0_pro']
TEMPERATURE = config['llm']['temperature']
RESPONSE_WORD_MIN = config['response']['word_min']

async def create_research_plan(state: AgentState, *, config: RunnableConfig) -> dict[str, list[str] | str]:
    class Plan(BaseModel):
        """Generate research plan."""
        steps: list[str] = Field(description="the list of research steps")
    model = ChatGoogleGenerativeAI(model=GEMINI_2_0_FLASH, temperature=TEMPERATURE, streaming=True)
    messages = [
        {"role": "system", "content": RESEARCH_PLAN_SYSTEM_PROMPT}
    ] + state.messages

    logging.info("---PLAN GENERATION---")
    print(await model.with_structured_output(Plan).ainvoke(messages))
    response = cast(Plan, await model.with_structured_output(Plan).ainvoke(messages))
    return {"steps": response.steps}

async def conduct_research(state: AgentState, *, config: RunnableConfig):
    result = await research_graph.ainvoke({"question": state.steps[0]})
    documents = result["documents"]
    step = state.steps[0]
    logger.info(f"\n{len(documents)} documents retrived in total for the step: {step}")
    return {"steps": state.steps[1:], "documents": documents}

def check_research_finished(state: AgentState, *, config: RunnableConfig):
    if len(state.steps) > 0:
        return "conduct_research"
    else:
        return "respond"

def check_finished(state: AgentState, *, config: RunnableConfig):
    if state.hallucination.binary_score == "1":
        return "END"
    else:
        return "conduct_research"

def _format_doc(doc: Document):
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"

def _format_docs(docs: Optional[list[Document]]):
    if not docs:
        return "<documents></documents>"
    formatted_docs = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
    {formatted_docs}
</documents>
"""

async def respond(state: AgentState, *, config: RunnableConfig):
    logger.info("---REPONSE GENERATION STEP---")
    model = ChatGoogleGenerativeAI(model=GEMINI_2_0_PRO, temperature=TEMPERATURE, streaming=True)
    context = _format_docs(state.documents)
    prompt = RESPONSE_SYSTEM_PROMPT.format(context=context, word_min=RESPONSE_WORD_MIN)
    messages = [
        {"role": "system", "content": prompt},
    ] + state.messages
    response = await model.ainvoke(messages)

    return {"messages": [response]}

async def check_hallucinations(state: AgentState, *, config: RunnableConfig):
    logger.info("---CHECK HALLUCINATIONS---")
    model = ChatGoogleGenerativeAI(model=GEMINI_2_0_FLASH, temperature=TEMPERATURE, streaming=True)
    system_prompt = CHECK_HALLUCINATIONS.format(
        documents=state.documents,
        generation=state.messages[-1]
    )
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state.messages
    response = cast(HalluciantionGrade, await model.with_structured_output(HalluciantionGrade).ainvoke(messages))
    logger.info(f"Hallucination grade: {response.binary_score}")
    return {"hallucination": response}

memory = MemorySaver()
graph_builder = StateGraph(AgentState, input=InputState)
graph_builder.add_node(create_research_plan)
graph_builder.add_node(conduct_research)
graph_builder.add_node(respond)
graph_builder.add_node(check_hallucinations)
graph_builder.add_edge(START, "create_research_plan")
graph_builder.add_edge("create_research_plan", "conduct_research")
graph_builder.add_conditional_edges("conduct_research", check_research_finished, {"respond": "respond", "conduct_research": "conduct_research"})
graph_builder.add_edge("respond", "check_hallucinations")
graph_builder.add_conditional_edges("check_hallucinations", check_finished, {"conduct_research": "conduct_research", "END": END})
graph = graph_builder.compile(checkpointer=memory)