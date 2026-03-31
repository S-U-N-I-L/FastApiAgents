from dataclasses import dataclass
from operator import add
from os import name
from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langgraph.constants import START
from langgraph.graph import StateGraph, add_messages
from pydantic import BaseModel


def mul(x: int, y: int) -> int:
    print(f'multiplying {x} and {y}')
    return x * y

## you can use TypeDict base classes or pydantic base model as state
class State(TypedDict):
    messages: str

def node_a(state: State):
    print(state.state, ' is current state now adding from node1')
    return {'state': ['adding node a']}


graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")



print(graph.compile().invoke(GraphStatePydantic(state=["initial message"])))


#trying messages witth id

messages = [HumanMessage("human message hey hi how are u ", name="sunil", id=1),
HumanMessage("human message hey hi how are u ", name="sunil", id=3),
            AIMessage("ai message", id=4)]
overrite = HumanMessage("this will overwrite", id=2)

messages = add_messages(messages, overrite)


delete  = [RemoveMessage(id=m.id) for m in messages[:-2]]

print(delete)
messages = add_messages(messages, delete)
for m in messages:
    print(m)

