from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph




class OverAllSchema(TypedDict):
    user_id: str
    query: str
    internal_logs: list[str]
    final_answer: str

class InputSchema(TypedDict):
    user_id: str
    query: str
    location: str

class OutputSchema(TypedDict):
    final_answer: str
    somestring: str

def process_query(state: InputSchema):
    print(state)
    print(f'processing query {state["query"]} for user {state["user_id"]}')


def node1(state: InputSchema) -> OutputSchema:
    print(state["location"], 'in node 1')
    return {'final_answer': 'final_answer'}


builder = StateGraph(state_schema=OverAllSchema, input_schema=InputSchema, output_schema=OutputSchema)
builder.add_node(process_query)
builder.add_node(node1)
builder.add_edge(START, "process_query")
builder.add_edge("process_query", "node1")
builder.add_edge("node1", END)

graph = builder.compile()

response = graph.invoke({'user_id':'ss', 'query':'tell me about myself','location':'ddd'})
print(response)

