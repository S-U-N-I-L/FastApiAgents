import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional, List

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)






# Conversation
conversation = [HumanMessage(content="Hi, I'm Sunil."),
                AIMessage(content="Nice to meet you, Sunil."),
                HumanMessage(content="I really like biking around San Francisco.")]

from trustcall import create_extractor

# Schema
class UserProfile(BaseModel):
    """User profile schema with typed fields"""
    user_name: str = Field(description="The user's preferred name")
    interests: List[str] = Field(description="A list of the user's interests")



# Create the extractor
trustcall_extractor = create_extractor(
    model,
    tools=[UserProfile],
    tool_choice="UserProfile"
)

# Instruction
system_msg = "Extract the user profile from the following conversation"

# Invoke the extractor
result = trustcall_extractor.invoke({"messages": [SystemMessage(content=system_msg)]+conversation})

for m in result["messages"]:
    m.pretty_print()

schema = result["responses"]
print(f'schema {schema}')

print(f" model dump {schema[0].model_dump()}")

# Update the conversation
updated_conversation = [HumanMessage(content="Hi, I'm Sunil."),
                        AIMessage(content="Nice to meet you, Sunil."),
                        HumanMessage(content="I really like biking around San Francisco."),
                        AIMessage(content="San Francisco is a great city! Where do you go after biking?"),
                        HumanMessage(content="I really like to go to a bakery after biking."),]

# Update the instruction
system_msg = f"""Update the memory (JSON doc) to incorporate new information from the following conversation"""

# Invoke the extractor with the updated instruction and existing profile with the corresponding tool name (UserProfile)
result = trustcall_extractor.invoke({"messages": [SystemMessage(content=system_msg)]+updated_conversation},
                                    {"existing": {"UserProfile": schema[0].model_dump()}})


for m in result["messages"]:
    m.pretty_print()


