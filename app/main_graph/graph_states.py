from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.messages import AnyMessage
from langchain_core.documents import Document
from langgraph.graph import add_messages

from pydantic import BaseModel, Field

from app.utils.utils import reduce_docs

@dataclass(kw_only=True)
class InputState:
    messages: Annotated[AnyMessage, add_messages]

class HalluciantionGrade(BaseModel):
    binary_score: str = Field(
        description="Answer is grounded in the facts, '1' or '0'"
    )


@dataclass(kw_only=True)
class AgentState(InputState):
    steps: list[str] = field(default_factory=list)
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    hallucination: HalluciantionGrade = field(default_factory=lambda: HalluciantionGrade(binary_score="0"))