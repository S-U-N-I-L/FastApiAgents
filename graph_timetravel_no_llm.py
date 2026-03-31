import os
import textwrap
from os import name

from anyio.lowlevel import checkpoint
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt


class MyGraphState(MessagesState):
    pass



def node1(state: MyGraphState):
    print("node 1 --- ")
    return {"messages": [HumanMessage("node 1 added this",name="sunil")]}

def node2(state: MyGraphState):
    print("node 2 --- ")
    # msg = state["messages"][-1]
    # if len(msg.content) > 10:
    #     raise interrupt(f'node interrupted')

    return {"messages": [HumanMessage("node 2 added this",name="sunil")]}

def node3(state: MyGraphState):
    print("node 3 --- ")
    return {"messages": [HumanMessage("node 3 added this",name="sunil")]}

def node4(state: MyGraphState):
    print("node 4 --- ")
    return state


builder = StateGraph(MyGraphState)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("node3", node3)
builder.add_node("node4", node4)

builder.add_edge(START, "node1")
builder.add_edge("node1","node2")
builder.add_edge("node2","node3")
builder.add_edge("node3","node4")
builder.add_edge("node4",END)


memory = MemorySaver()

actualGraph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id":"1333"}}




for event in actualGraph.stream(
        {"messages": [HumanMessage("please multiply 5 and 5",name="sunil")]},
        config=config,
        stream_mode="values"):
    event['messages'][-1].pretty_print()



allstates = [s for s in actualGraph.get_state_history(config)]

# print('total states ' , len(allstates))
# for state in reversed(allstates):
#     print('------------------------' * 10)
#     print('state --> ', state.config)
#     print('values --> ', state.values['messages'])
#     print('------------------------' * 10)
#
# print('whats is there at node 2')
# print('------------------------' * 10)
# print('state --> ', allstates[2].config)
# print('values --> ', allstates[2].values['messages'])
# print('------------------------' * 10)

print('lets start graph from 2 checkpoint')

for event in actualGraph.stream(
        None,
        config=allstates[2].config,
        stream_mode="values"):
    event['messages'][-1].pretty_print()


initial_msg = allstates[-2]

print(f'updating {initial_msg.values['messages'][0].id}')
print(f' config {initial_msg.config}')

fork_config = actualGraph.update_state(
    initial_msg.config,
    {"messages": [HumanMessage(content='multiply by 4 and 3', id=initial_msg.values['messages'][0].id)]}
)

print('forked look after it')

for event in actualGraph.stream(
        None,
        config=config,
        stream_mode="values"):
    event['messages'][-1].pretty_print()
# Generate a PNG imageaa

png_data = actualGraph.get_graph().draw_mermaid_png()

# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)
