import asyncio
import sqlite3
import time
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END

# 1. Define your State
class State(TypedDict):
    # 'Annotated' with a list tells LangGraph to APPEND messages rather than overwrite
    messages: Annotated[list, lambda x, y: x + y]
    summary: str

# 2. Define Nodes
def node_1(state: State):
    return {"messages": ["Node 1: I finished instantly!"]}

def node_2(state: State):
    time.sleep(1)  # Simulate a long-running process
    return {"summary": "Node 2: I'm done after sleeping."}

def node_3(state: State):
    time.sleep(2)
    return {"messages": ["Node 3: Final step complete."]}

## connect to db
db_path = "statedb/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# Create a thread
config = {"configurable": {"thread_id": "123"}}

# 3. Build the Graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")
builder.add_edge("node_3", END)

graph = builder.compile()



# 4. Stream the results
inputs = {"messages": ["User: Hello"], "summary": "No summary yet"}


async def call_astrem():
    async for event in graph.astream_events(inputs, version="v2"):
        print(f"event {event['event']} meta data. {event['metadata']} event name {event['name']}. data {event['data']}")

# 5. The "Main" block to run the script
if __name__ == "__main__":

    print("--- Starting Stream mode is updates ---")
    for chunk in graph.stream(inputs,  stream_mode="updates"):
        # Each 'chunk' is a dictionary: { "node_name": { "updated_key": "value" } }
        for node_name, updates in chunk.items():
            print(f"\n[EVENT] Node '{node_name}' just finished! updates {updates}")
            if "messages" in updates:
                print(f"New Message: {updates['messages'][-1]}")
            if "summary" in updates:
                print(f"Summary Update: {updates['summary']}")


    print("--- Starting Stream mode is values we get whole state---")
    for state in graph.stream(inputs, stream_mode="values"):
        print("state", state)


    print("--- Starting Stream mode is messages---")
    for msg, metadata in graph.stream(inputs,{'configurable': {'thread_id':'444'}}, stream_mode="messages"):
        # msg is an AIMessageChunk
        # metadata contains 'langgraph_node', 'langgraph_step', etc.

        # Print the text as it arrives without a newline
        print(msg.content, end="|", flush=True)

        # You can still see which node is talking
        node_name = metadata.get("langgraph_node")

    print("--- Starting Stream astream ---")
    asyncio.run(call_astrem())


