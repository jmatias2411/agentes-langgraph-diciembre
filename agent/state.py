import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # 'messages' acumula el historial. 'operator.add' combina la lista vieja con la nueva.
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # 'next' guarda la decisión de a quién le toca trabajar
    next: str