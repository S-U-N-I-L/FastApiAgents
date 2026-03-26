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

def get_user_food_pref() :
    '''this gives users food preferences'''
    print('food pref ')
    return 'mexican'

def get_user_color_pref() :
    '''this gives users color preferences'''
    print('color pref ')
    return 'blue color'

def add(x,y) :
    '''this gives sum of a and b'''
    print('adding ')
    return x+y

def mul(x,y) :
    '''multiply x and y'''
    print('multiplying ')
    return x*y

def div(x,y) :
    '''divide x and y'''
    print('dividing ')
    return x/y

sys = SystemMessage("You are a helpful assistant tasked with giving user preference like food and color, also can add, mul, and div")

client = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)
run = client.bind_tools([get_user_food_pref, get_user_color_pref, add, mul, div])

class MyGraphState(MessagesState):
    pass



def node1(state: MyGraphState):
    print("node1 called ", state)
    return {"messages": run.invoke(state['messages'])}


builder = StateGraph(MyGraphState)
builder.add_node("node1",node1)
builder.add_node("tools", ToolNode([get_user_food_pref, get_user_color_pref, add, mul, div]))


builder.add_edge(START, "node1")
builder.add_conditional_edges("node1",
                              # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
                              # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
                              tools_condition,
                              )
builder.add_edge("tools", "node1")

memory = MemorySaver()

actualGraph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id":"1"}}

messages = actualGraph.invoke({"messages":[sys] + [HumanMessage("add 5 and 7",name="sunil")]},config=config)

for m in messages["messages"]:
    m.pretty_print()


messages = actualGraph.invoke({"messages":[sys] + [HumanMessage("now multply by 2",name="sunil")]},config=config)

for m in messages["messages"]:
    m.pretty_print()

messages = actualGraph.invoke({"messages":[sys] + [HumanMessage("divide by 2",name="sunil")]},config=config)

for m in messages["messages"]:
    m.pretty_print()

messages = actualGraph.invoke({"messages":[sys] + [HumanMessage("hello my name is sunil")]},config=config)

for m in messages["messages"]:
    m.pretty_print()

messages = actualGraph.invoke({"messages":[sys] + [HumanMessage("tell me who am i")]},config=config)

for m in messages["messages"]:
    m.pretty_print()

# Generate a PNG image
png_data = actualGraph.get_graph().draw_mermaid_png()

# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)
