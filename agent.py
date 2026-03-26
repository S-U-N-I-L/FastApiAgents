import os

from keyring.core import load_env
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel




# 1. Setup the Model
# PydanticAI automatically looks for 'GEMINI_API_KEY' in your environment
model = GeminiModel('gemini-3-flash-preview')

# 2. Define the structured response we want from the Agent
class AgentResponse(BaseModel):
    answer: str
    is_pro_user: bool

# 3. Create the Agent
agent = Agent(
    model,
    output_type=AgentResponse,
    system_prompt=(
        "You are a helpful assistant for a SaaS platform. "
        "Always check the user's subscription status using the tool provided before answering."
        "Always check the user's food preference using the tool provided before answering."
        "Always check the user's location preference using the tool provided before answering."
        "Always check the user's language preference using the tool provided before answering."
    )
)

# 4. Define a Tool (The Agent will "decide" to call this)
@agent.tool
async def get_user_tier(ctx: RunContext[str], user_id: str) -> str:
    """Checks if the user has a 'free' or 'pro' account."""
    # Simulation: In a real app, you'd query your database here
    print('using tool to query user')
    mock_db = {"user_123": "pro", "user_456": "free"}
    return mock_db.get(user_id, "free")

@agent.tool
async def get_user_joke_pref(ctx: RunContext[str], user_id: str) -> str:
    '''checks if the user have a language preference available for listening a joke.
    this function returns current users preferred language, that's the language he want to listen joke in'''
    print('using tool to query user joke preference')
    mock_db = {"user_123": "english", "user_456": "hindi", 'user_789': 'spanish'}
    return mock_db.get(user_id, "english")

@agent.tool
async def get_user_food_liking(ctx: RunContext[str], user_id: str) -> str:
    """checks what kind of food a user like, may be italian, mexican, indian etc"""
    print('using tool to query user food preference')
    mock_db = {"user_123": "mexican", "user_456": "italian", 'user_789': 'continental'}
    return mock_db.get(user_id, "mexican")

@agent.tool
async def get_user_location_preference(ctx: RunContext[str], user_id: str) -> str:
    """checks where the user lives, in which city"""
    print('using tool to query user location preference')
    mock_db = {"user_123": "chicago", "user_456": "newyork", 'user_789': 'california'}
    print('will return', mock_db.get(user_id))
    return mock_db.get(user_id, "mexican")