import os

from dotenv import load_dotenv
from fastapi import Path
from keyring.core import load_env



GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    print('--------------- not found ')


# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# LangGraph
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


# --- 1. MOCK DATABASE ---
USER_DATABASE = {
    "user_1": {"name": "Arjun", "pref": "Spicy Indian or Thai"},
    "user_2": {"name": "Sara", "pref": "Vegan Italian"},
    "user_3": {"name": "Chen", "pref": "Japanese Sushi"}
}

# --- 2. TOOLS ---
@tool
def lookup_user_profile(user_id: str):
    """Retrieves a user's name and food preferences from the internal database."""
    profile = USER_DATABASE.get(user_id)
    if not profile:
        return "User not found in database. Ask the user for their preference."
    return f"User Name: {profile['name']}, Preferences: {profile['pref']}"

tools = [lookup_user_profile]

# --- 3. AGENT SETUP ---
# UPDATED: Using the gemini-3-flash-preview model
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.7,
    google_api_key=GEMINI_KEY
)

memory = MemorySaver()
agent_executor = create_react_agent(llm, tools, checkpointer=memory)