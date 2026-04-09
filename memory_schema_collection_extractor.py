import os
import uuid
from typing import TypedDict, List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import accepts_config
from langgraph.store.base import BaseStore
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

in_memory_store = InMemoryStore()

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

class Memory(BaseModel):
    content : str = Field(description="The main content of the memory. For example: User expressed interest in learning about French.")

class MemoryCollection(BaseModel):
    memories: List[Memory] = Field(description="A list of memories about the user.")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)



from trustcall import create_extractor

# Create the extractor
trustcall_extractor = create_extractor(
    llm,
    tools=[Memory],
    tool_choice="Memory",
    enable_inserts=True,
)

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Instruction
instruction = """Extract memories from the following conversation:"""

# Conversation
conversation = [HumanMessage(content="Hi, I'm Sunil."),
                AIMessage(content="Nice to meet you, Sunil."),
                HumanMessage(content="This morning I had a nice bike ride in San Francisco.")]

# Invoke the extractor
result = trustcall_extractor.invoke({"messages": [SystemMessage(content=instruction)] + conversation})

# Messages contain the tool calls
for m in result["messages"]:
    m.pretty_print()

# Responses contain the memories that adhere to the schema
for m in result["responses"]:
    print(m)

# # Update the conversation
# updated_conversation = [AIMessage(content="That's great, did you do after?"),
#                         HumanMessage(content="I went to Tartine and ate a croissant."),
#                         AIMessage(content="What else is on your mind?"),
#                         HumanMessage(content="I was thinking about my Japan, and going back this winter!"),]
#
# # Update the instruction
# system_msg = """Update existing memories and create new ones based on the following conversation:"""
#
# # We'll save existing memories, giving them an ID, key (tool name), and value
# tool_name = "Memory"
# existing_memories = [(str(i), tool_name, memory.model_dump()) for i, memory in enumerate(result["responses"])] if result["responses"] else None
# print(f'existing memory {existing_memories}')
#
# # Invoke the extractor with our updated conversation and existing memories
# result = trustcall_extractor.invoke({"messages": updated_conversation,
#                                      "existing": existing_memories})

# # Messages from the model indicate two tool calls were made
# print('---- messages ----')
# for m in result["messages"]:
#     m.pretty_print()
#
# # Responses contain the memories that adhere to the schema
# print('-----respnose-----')
# for m in result["responses"]:
#     print(m)