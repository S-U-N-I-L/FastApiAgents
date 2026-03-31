from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END

# 1. Setup Graph
class State(MessagesState): pass

def node1(s): return {"messages": [HumanMessage("N1 Data")]}
def node2(s): return {"messages": [HumanMessage("N2 Data")]}
def node3(s): return {"messages": [HumanMessage("N3 Data")]}

builder = StateGraph(State)
builder.add_node("node1", node1); builder.add_node("node2", node2); builder.add_node("node3", node3)
builder.add_edge(START, "node1"); builder.add_edge("node1", "node2"); builder.add_edge("node2", "node3"); builder.add_edge("node3", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "test_123"}}

# 2. Initial Full Run
print("--- ROUND 1: INITIAL RUN ---")
for event in graph.stream({"messages": [HumanMessage("Start")]}, config, stream_mode="values"):
    print(f"Node: {list(event.keys())}, Last Msg: {event['messages'][-1].content}")

# 3. Time Travel: Find the state AFTER Node 2 finished
history = list(graph.get_state_history(config))

print(f'lenght after fist rurn {len(history)}')
# We want the checkpoint where 'node3' is the NEXT scheduled node
to_fork = next(s for s in history if s.next == ("node3",))

# 4. Forking: Update the state at that specific checkpoint
print("\n--- FORKING AT NODE 2 ---")
# This creates a NEW latest checkpoint for this thread_id
graph.update_state(
    to_fork.config,
    {"messages": [HumanMessage("FORKED DATA", id=to_fork.values['messages'][-1].id)]}
)

# 5. Resume using .stream() with the general config
# It will automatically pick up the new "Forked" latest checkpoint
print("\n--- ROUND 2: RESUMING FROM FORK ---")
for event in graph.stream(None, config, stream_mode="values"):
    # Notice it starts at Node 3 and skips 1 & 2
    print(f"Node: {list(event.keys())}, Last Msg: {event['messages'][-1].content}")

print(f'lenght after second rurn {len(history)}')

# Get the full history
all_history = list(graph.get_state_history(config))
print(f"Total Checkpoints in Thread: {len(all_history)}")

print("\n--- CHECKPOINT LINEAGE ---")
print(f"{'Node Next':<15} | {'Checkpoint ID':<15} | {'Parent ID':<15}")
print("-" * 50)

for state in reversed(all_history):
    # Get short IDs for readability
    cp_id = state.config["configurable"]["checkpoint_id"][-4:]
    # Not all states have a parent (the first one doesn't)
    parent_id = state.config["configurable"].get("checkpoint_ns", "START")[-4:]

    # .next tells you what node is about to run
    next_node = str(state.next[0]) if state.next else "END"

    print(f"{next_node:<15} | {cp_id:<15} | {parent_id:<15}")
