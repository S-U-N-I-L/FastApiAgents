import os
from os import name
from typing import TypedDict, Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import state, StateGraph, START, END, MessagesState
from openai.types import Image
from rich.jupyter import display


## create the state first
class GraphState(TypedDict):
    currentState: str





## now smoe nodes
def node1(state:GraphState):
    print('i m node1 ')

def node2(state:GraphState):
    print('i m node2 ')

def node3(state:GraphState):
    print('i m node3 ')


def condition_edge(state:GraphState) -> Literal["node2", "node3"]:
    if state["currentState"] == "node2":
        return "node2"
    return "node3"


builder = StateGraph(GraphState)
builder.add_node(node1)
builder.add_node(node2)
builder.add_node(node3)

builder.add_edge(START, "node1")
builder.add_conditional_edges("node1", condition_edge)
builder.add_edge("node2", END)
builder.add_edge("node3", END)


actualGraph = builder.compile()




messages = [AIMessage("you said you want top cities in india", name="Model")]
messages.append(HumanMessage("yes thats right", name="sunil"))
messages.append(AIMessage("ok here is the list ", name="Model"))

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")



# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

def get_user_food_pref() :
    '''this gives users food preferences'''
    print('food pref ')
    return 'mexican'

client = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)
run = client.bind_tools([get_user_food_pref],tool_choice="get_user_food_pref")


response = run.invoke([HumanMessage("ok give user1 food preference", name="Sunil")])
print(response)


