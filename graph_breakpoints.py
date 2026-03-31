import os
from os import name

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

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

client = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey, )
llm = client.bind_tools([get_user_food_pref, get_user_color_pref, add, mul, div])

class MyGraphState(MessagesState):
    pass

def human_feedback(state: MyGraphState):
    print('human feedback node ')
    return state

def assistance(state: MyGraphState):
    print("assistance node calling llm ", state)
    return {"messages": llm.invoke(state['messages'])}


builder = StateGraph(MyGraphState)
builder.add_node("human_feedback", human_feedback)
builder.add_node("assistance",assistance)
builder.add_node("tools", ToolNode([get_user_food_pref, get_user_color_pref, add, mul, div]))


builder.add_edge(START, "human_feedback")
builder.add_edge( "human_feedback","assistance")
builder.add_conditional_edges("assistance", tools_condition,
                              {
                                  "tools" :"tools",
                              "__end__": "human_feedback"})
builder.add_edge( "tools", "assistance")

memory = MemorySaver()

actualGraph = builder.compile(checkpointer=memory, interrupt_before=['human_feedback'] )

config = {"configurable": {"thread_id":"1333"}}




for event in actualGraph.stream(
        {"messages":[sys] + [HumanMessage("please multiply 5 and 5",name="sunil")]},
        config=config,
        stream_mode="values"):
    event['messages'][-1].pretty_print()



user_input = input('enter what you want')
msgs = actualGraph.get_state(config)
clear_lastmsg = msgs.values['messages'][-1]




actualGraph.update_state(config,{'messages':[RemoveMessage(clear_lastmsg.id), HumanMessage(user_input,name="sunil")]})
#
# print(f'printing user input {user_input}')






for event in actualGraph.stream(None,config, stream_mode="values"):
     event['messages'][-1].pretty_print()




# Generate a PNG image

png_data = actualGraph.get_graph().draw_mermaid_png()

# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)
