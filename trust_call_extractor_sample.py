import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from trustcall import create_extractor
from pydantic import BaseModel, Field

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

# Inspect the tool calls made by Trustcall
class Spy:
    def __init__(self):
        self.called_tools = []

    def __call__(self, run):
        # Collect information about the tool calls made by the extractor.
        q = [run]
        print(f'q is {q}')
        print(f'run is {run}')

        while q:
            r = q.pop()
            if r.child_runs:
                q.extend(r.child_runs)
            if r.run_type == "chat_model":
                self.called_tools.append(
                    r.outputs["generations"][0][0]["message"]["kwargs"]["tool_calls"]
                )

# Initialize the spy
spy = Spy()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)

# 1. Define your schema
class UserProfile(BaseModel):
    name: str = Field(description="The user's name")
    interests: list[str] = Field(default_factory=list, description="List of user interests")

# 2. Create the extractor
# It uses the LLM and the schema to prepare the 'patching' logic
extractor = create_extractor(llm, tools=[UserProfile], tool_choice="UserProfile")

# Add the spy as a listener
trustcall_extractor_see_all_tool_calls = extractor.with_listeners(on_end=spy)
result = extractor.invoke({
    "messages": [("user", "Hi my name is alice and i like cooking")]
})

print(f' metadata without existing {result['response_metadata']}')

# 3. Update existing memory with a DELTA
existing_memory = {"name": "Alice", "interests": ["Python"]}
new_info = "Alice also likes hiking and swimming."

# Trustcall sends the existing_memory to the LLM and asks for patches
result = extractor.invoke({
    "messages": [("user", new_info)],
    "existing": {"UserProfile": result['responses'][0].model_dump()}
})

# Result will contain the updated profile without Alice having to re-list 'Python'
updated_profile = result["responses"][0]

print(f'profile: {updated_profile}')
print(f'last message {result['messages'][-1]}')
print(f'metadata {result["response_metadata"]}')
# Output: {'name': 'Alice', 'interests': ['Python', 'hiking', 'swimming']}

result = trustcall_extractor_see_all_tool_calls.invoke({
    "messages": [("user", "Actually, I don't like Swimming anymore. Please remove it and add flying jets and painting, oh sorry not painting i meant sketching")],
    "existing": {"UserProfile": result['responses'][0].model_dump()}
})

print('final memory',result["responses"][0])
print(f'last message {result['messages'][-1]}')
print(f'metadata {result["response_metadata"]}')


def extract_tool_info(tool_calls, schema_name="Memory"):
    """Extract information from tool calls for both patches and new memories.

    Args:
        tool_calls: List of tool calls from the model
        schema_name: Name of the schema tool (e.g., "Memory", "ToDo", "Profile")
    """

    # Initialize list of changes
    changes = []

    for call_group in tool_calls:
        for call in call_group:
            if call['name'] == 'PatchDoc':
                changes.append({
                    'type': 'update',
                    'doc_id': call['args']['json_doc_id'],
                    'planned_edits': call['args']['planned_edits'],
                    'value': call.get('args', {}).get('patches', [{}])[0].get('value') if call.get('args', {}).get('patches') else None

                })
            elif call['name'] == schema_name:
                changes.append({
                    'type': 'new',
                    'value': call['args']
                })

    # Format results as a single string
    result_parts = []
    for change in changes:
        if change['type'] == 'update':
            result_parts.append(
                f"Document {change['doc_id']} updated:\n"
                f"Plan: {change['planned_edits']}\n"
                f"Added content: {change['value']}"
            )
        else:
            result_parts.append(
                f"New {schema_name} created:\n"
                f"Content: {change['value']}"
            )

    return "\n\n".join(result_parts)
changes = extract_tool_info(spy.called_tools, "UserProfile")

print(changes)