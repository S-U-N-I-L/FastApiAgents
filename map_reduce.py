import operator
import os
from typing import TypedDict, Annotated

from docutils.nodes import topic
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Send
from pydantic import BaseModel

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)

## prompts
subjects_prompts = """Generate a comma separated list of between 2 to 3 examples related to {topic} """
joke_prompt = """ generate a joke about {subject} """
best_joke_prompt = """Below are a bunch of jokes about {topic}. Select the best one! Return the ID of the best one, starting 0 as the ID for the first joke. Jokes: \n\n  {jokes}"""


class Subjects(BaseModel):
    subjects: list[str]


class BestJoke(BaseModel):
    id: int


class OverallState(TypedDict):
    topic: str
    subjects: list
    jokes: Annotated[list, operator.add]
    best_selected_joke: str

def generate_subjects(state : OverallState):
    prompt = subjects_prompts.format(topic = state['topic'])
    response = model.with_structured_output(Subjects).invoke(prompt)
    print(f'subjects {response.subjects}')
    return {"subjects": response.subjects}

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject":s}) for s in state['subjects']]


class JokeState(TypedDict):
    subject: str

class Joke(BaseModel):
    joke: str

def generate_joke(state: JokeState):
    prompt = joke_prompt.format(subject = state['subject'])
    response = model.with_structured_output(Joke).invoke(prompt)
    print(f' generated joke for {state["subject"]} - {response.joke}')
    return {"jokes": [response.joke]}

def best_joke(state:OverallState):
    prompt = best_joke_prompt.format(topic = state['topic'], jokes = state['jokes'])
    response = model.with_structured_output(BestJoke).invoke(prompt)
    return {"best_selected_joke": state['jokes'][response.id]}

builder = StateGraph(OverallState)
builder.add_node("generate_subjects", generate_subjects)
builder.add_node("generate_joke", generate_joke)
builder.add_node("best_joke", best_joke)

builder.add_edge(START, "generate_subjects")
builder.add_conditional_edges( "generate_subjects",continue_to_jokes, ["generate_joke"])
builder.add_edge("generate_joke", "best_joke")
builder.add_edge("best_joke", END)

graph = builder.compile();

response = graph.invoke({"topic":"Shah Rukh Khan"})
print(response['best_selected_joke'])

png_data = graph.get_graph().draw_mermaid_png()
# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)

