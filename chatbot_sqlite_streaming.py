import os
from os import name

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")



# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

sys = SystemMessage("You are a helpful assistant tasked with giving user preference like food and color, also can add, mul, and div")

client = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)

class MyGraphState(MessagesState):
    summary: str


def call_model(state: MyGraphState):
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it
    if summary:

        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    response = client.invoke(messages)
    return {"messages": response}


def summarize_conversation(state: MyGraphState):
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt
    if summary:

        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )

    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = client.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


from langgraph.graph import END
from typing_extensions import Literal


# Determine whether to end or summarize the conversation
def should_continue(state: MyGraphState) -> Literal["summarize_conversation", END]:
    """Return the next node to execute."""

    messages = state["messages"]

    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"

    # Otherwise we can just end
    return END


import sqlite3
from langgraph.graph import StateGraph, START

## connect to db
db_path = "statedb/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# Define a new graph
workflow = StateGraph(MyGraphState)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile

graph = workflow.compile(checkpointer=memory)




png_data = graph.get_graph().draw_mermaid_png()



# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)

# Create a thread
config = {"configurable": {"thread_id": "1"}}

# messages = graph.invoke({"messages":[sys] + [HumanMessage("hi remember i asked about eating something",name="sunil")]},config=config)
# print(messages)
# print("#######" * 20)
# messages = graph.invoke({"messages":[sys] + [HumanMessage("lets play a game",name="sunil")]},config=config)
# print(messages)
# print("#######" * 20)
# messages = graph.invoke({"messages":[sys] + [HumanMessage("which game ",name="sunil")]},config=config)
# print(messages)
# print("#######" * 20)
# messages = graph.invoke({"messages":[sys] + [HumanMessage("cricket",name="sunil")]},config=config)
# print(messages)
# print("#######" * 20)
# messages = graph.invoke({"messages":[sys] + [HumanMessage("suggest some movie",name="sunil")]},config=config)
# print(messages)
# print("#######" * 20)
# messages = graph.invoke({"messages":[sys] + [HumanMessage("suggest a movie horror",name="sunil")]},config=config)
# print(messages)
# print("#######" * 20)


for event in graph.stream({"messages": [HumanMessage("any suggestions to get a pet")]}, config, stream_mode="values"):
    print(event)
