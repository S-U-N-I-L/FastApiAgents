import os
import uuid

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, merge_message_runs, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from trustcall import create_extractor
from pydantic import BaseModel, Field





# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")



llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)

# 1. Define your schema
class Memory(BaseModel):
    content: str = Field("just content for a user. For example: User expressed interest in learning about French.")

# 2. Create the extractor
# It uses the LLM and the schema to prepare the 'patching' logic
extractor = create_extractor(llm, tools=[Memory], tool_choice="Memory", enable_inserts=True)



# Chatbot instruction
MODEL_SYSTEM_MESSAGE = """You are a helpful chatbot. You are designed to be a companion to a user. 

You have a long term memory which keeps track of information you learn about the user over time.

Current Memory (may include updated memories from this conversation): 

{memory}"""

# Trustcall instruction
TRUSTCALL_INSTRUCTION = """Reflect on following interaction. 

Use the provided tools to retain any necessary memories about the user. 

Use parallel tool calling to handle updates and insertions simultaneously:"""

def call_model(state: MessagesState, config: RunnableConfig, store: BaseStore):
    #lets get the existing memory
    user_id = config['configurable']['user_id']
    name_space = ('memory', user_id)
    memories = store.search(name_space)
    # Format the memories for the system prompt
    info = "\n".join(f"- {mem.value['content']}" for mem in memories)
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=info)
    response = llm.invoke([SystemMessage(system_msg)] + state['messages'])
    return {'messages': response}

def write_memory(state: MessagesState, config: RunnableConfig, store: BaseStore):
    # lets get the existing memory
    user_id = config['configurable']['user_id']
    name_space = ('memory', user_id)
    existing_items = store.search(name_space)

    # Format the existing memories for the Trustcall extractor
    tool_name = "Memory"
    existing_memories = ([(existing_item.key, tool_name, existing_item.value)
                          for existing_item in existing_items]
                          if existing_items
                          else None
                        )

    # Merge the chat history and the instruction
    updated_messages = list(
        merge_message_runs(messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION)] + state["messages"]))
    result = extractor.invoke({"messages":updated_messages,
                                "existing": existing_memories})

    # Save the memories from Trustcall to the store
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(name_space,
                  rmeta.get("json_doc_id", str(uuid.uuid4())),
                  r.model_dump(mode="json"),
                  )


# Define the graph
builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("write_memory", write_memory)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "write_memory")
builder.add_edge("write_memory", END)

# Store for long-term (across-thread) memory
across_thread_memory = InMemoryStore()

# Checkpointer for short-term (within-thread) memory
within_thread_memory = MemorySaver()

# Compile the graph with the checkpointer fir and store
graph = builder.compile(checkpointer=within_thread_memory, store=across_thread_memory)

if __name__ == "__main__":
    # We supply a thread ID for short-term (within-thread) memory
    # We supply a user ID for long-term (across-thread) memory
    print('------- first call--------')
    config = {"configurable": {"thread_id": "1", "user_id": "1"}}

    # User input
    input_messages = [HumanMessage(content="Hi, my name is Sunil")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()



    print('------- second call--------')
    config = {"configurable": {"thread_id": "1", "user_id": "1"}}

    # User input
    input_messages = [HumanMessage(content="Hi, i was in london for a week")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # User input
    input_messages = [HumanMessage(content="sorry , i was wrong not in london, i was in newyork and my name is Sonu, i like cooking")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    print('------finally memory---')
    # Namespace for the memory to save
    user_id = "1"
    namespace = ("memory", user_id)
    memories = across_thread_memory.search(namespace)
    for m in memories:
        print(m.dict())