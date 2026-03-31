import os
from os import name

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")



# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

import asyncio
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import BaseMessage, HumanMessage


# 1. Define the Graph State
class State(MessagesState):
    pass


# 2. Define the Node
llm = ChatOpenAI(model="gpt-4o", streaming=True, api_key=apikey)


async def call_model(state: State):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


# 3. Build the Graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

graph = workflow.compile()


# 4. Stream the Tokens
async def run_streaming_chat():
    inputs = {"messages": [HumanMessage(content="Explain async in 3 sentences.")]}

    print("AI Response: ", end="", flush=True)

    # version="v2" is the standard for modern LangGraph streaming
    async for chunk in graph.astream(inputs, stream_mode="messages", version="v2"):
        # data is a tuple: (MessageChunk, Metadata)
        msg, metadata = chunk["data"]

        # Filter for tokens: We want AIMessageChunks (partial)
        # and we want to ignore the final full AIMessage to avoid duplicates
        if chunk["type"] == "messages" and hasattr(msg, "content"):
            # Only print if it's a chunk (has a 'type' of 'AIMessageChunk')
            # and specifically from our 'agent' node
            if metadata.get("langgraph_node") == "agent":
                print(msg.content, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(run_streaming_chat())

