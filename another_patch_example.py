import json
import os

from dotenv import load_dotenv
from trustcall import create_extractor
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)

from typing import Dict, List, Optional

from pydantic import BaseModel




class User(BaseModel):
    preferred_name: str
    favorite_foods: List[str]
    age: int
    occupation: str
    favorite_color: Optional[str] = None
    languages: Dict[str, str] = {}

conversation = """Hi  I am alex, i started liking indian food now, somehow i am not liking sushi"""

initial_user = User(
    preferred_name="Alex",

    favorite_foods=["sushi", "pizza", "tacos", "ice cream", "pasta", "curry"],

    age=28,
    occupation="Software Engineer",

    favorite_color="blue",
    languages={"English": "native", "Spanish": "intermediate", "Python": "expert"},
)

#Naive approach
bound = model.bind_tools([User],
                        tool_choice="User")
naive_result = bound.invoke(
    f"""Update the memory (JSON doc) to incorporate new information from the following conversation:
<user_info>
{initial_user.model_dump()}
</user_info>
<convo>
{conversation}
</convo>"""
)
print("Naive approach result:")
naive_output = naive_result.model_dump()
print(naive_output)

# Trustcall approach
from trustcall import create_extractor

bound = create_extractor(model, tools=[User])

trustcall_result = bound.invoke(
    {
        "messages": [
SystemMessage(content=(
                "You are an expert at updating JSON documents using patches. "
                "When adding a new key to a dictionary (like a new language), "
                "use the 'add' operation. Only 'replace' keys that already exist."
            )),
            {
                "role": "user",
                "content": f"""Update the memory (JSON doc) to incorporate new information from the following conversation:
<convo>
{conversation}
</convo>""",
            }
        ],
        "existing": {"User": initial_user.model_dump()},
    }
)
print("\nTrustcall approach result:")
trustcall_output = trustcall_result["responses"][0].model_dump()
print(trustcall_output)

last_message = trustcall_result["messages"][-1]
for tool_call in last_message.tool_calls:
    if "patch" in tool_call["args"]:
        print("--- Patch Operations Detected ---")
        # You will see things like: {"op": "add", "path": "/hobbies/-", "value": "biking"}
        print(tool_call["args"]["patch"])

