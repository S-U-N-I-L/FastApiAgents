from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from typing_extensions import TypedDict
import uuid


# 1. Define State
class State(TypedDict):
    action: str
    approved: bool


# 2. Node with Interrupt
def approval_node(state: State):
    print("---Waiting for approval---")
    # This pauses execution. The value is sent to the user/client.
    is_approved = interrupt({
        "question": "Do you want to proceed with this action?",
        "details": state["action"]
    })

    # When resumed, `is_approved` will be the value passed back
    return {"approved": is_approved}


# 3. Build Graph
workflow = StateGraph(State)
workflow.add_node("approval_node", approval_node)
workflow.add_edge(START, "approval_node")
workflow.add_edge("approval_node", END)

# 4. Compile with Checkpointer
memory = InMemorySaver()
app = workflow.compile(checkpointer=memory)

# 5. Run it
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# First run: will pause at the interrupt
for event in app.stream({"action": "Delete database"}, config):
    print(event)

# 6. Resume from outside (e.g., human clicks 'Approve')
for event in app.stream(Command(resume=True), config):
    print(event)
