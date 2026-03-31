import operator
from typing import TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.errors import InvalidUpdateError
from langgraph.graph import StateGraph


def sort_list_reducer(current:list[str], updated:list[str]):
    current = current or []
    updated = updated or []
    return sorted(current + updated)

class State(TypedDict):
    state: Annotated[list,sort_list_reducer]

class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State):
        print(f'adding {self._value} to state {state['state']}')
        return {'state' : [self._value]}

builder = StateGraph(State)

builder.add_node("a", ReturnNodeValue("I am node A"))
builder.add_node("b", ReturnNodeValue("I am node B"))
builder.add_node("b2", ReturnNodeValue("I am node B2"))
builder.add_node("c", ReturnNodeValue("I am node C"))
builder.add_node("d", ReturnNodeValue("I am node D"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b2")
builder.add_edge(["b2","c"], "d")
builder.add_edge("d", END)

graph = builder.compile()

png_data = graph.get_graph().draw_mermaid_png()

try:
    result = graph.invoke({"state":['initial state']})
    print(result)
except InvalidUpdateError as e:
    print(e)


# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)