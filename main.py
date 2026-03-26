


import asyncio
import os

from google import genai
from keyring.core import load_env
from dotenv import load_dotenv



# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# 2. Load the specific .env file (e.g., .env.prod)
# This populates os.environ with values from that file
load_dotenv(f".env.{env}")

print('gemini key ', os.getenv("GEMINI_API_KEY"))


genai.api_key = os.getenv("GEMINI_API_KEY")

# Print all models that support generating content



# 3. Verification check
if not os.getenv("GEMINI_API_KEY"):
    print(f"⚠️ Warning: GEMINI_API_KEY not found in .env.{env}")

import time
from contextlib import asynccontextmanager
from typing import AsyncIterable


from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.sse import EventSourceResponse

from pydantic import BaseModel

from AppSettings import Settings, get_settings
from agent import AgentResponse, agent
from customer import customerRouter
from restaurant_agent import agent_executor, memory

from employee import Employee
from exception.ExceptionHandler import add_exception_handlers
from middleware.Middleware import middleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP TRACKING ---
    print("🚀 Application is starting up...")

    yield  # The app is running and handling requests here

    # --- SHUTDOWN TRACKING ---
    print("🛑 Application is shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(customerRouter)

add_exception_handlers(app)
middleware(app)


@app.get("/config")
def read_config(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "db": settings.database_url,
        "debug_mode": settings.debug
    }




@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)  # Pass the request to the next step
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print('process_time ', process_time)
    return response


@app.get("/hello/{name}")
async def say_hello(name: str):
    print('hello')
    return {"message": f"Hello {name}"}



class Item(BaseModel):
    name: str
    description: str | None


items = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]


@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        await asyncio.sleep(5)
        yield item


# In-memory storage for the scoreboard
scoreboard = {"home": 0, "away": 0}
# Event used to signal the stream that data has changed
update_event = asyncio.Event()


@app.get("/score/stream")
async def stream_score(request: Request):
    """The SSE endpoint that clients connect to."""

    async def event_generator():
        while True:
            # Check if the client disconnected to stop the loop
            if await request.is_disconnected():
                break

            # Send the current score
            yield {
                "data": scoreboard,
                "event": "score_update"
            }

            # Wait until the next update is triggered
            await update_event.wait()
            update_event.clear()

    return EventSourceResponse(event_generator())


@app.post("/score/update")
async def update_score(team: str, points: int):
    """Endpoint to update the score (e.g., from an admin panel)."""
    if team in scoreboard:
        scoreboard[team] += points
        # Trigger the event to notify all connected stream clients
        update_event.set()
        return {"status": "success", "new_score": scoreboard}
    return {"error": "Invalid team"}


class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/ask", response_model=AgentResponse)
async def ask_agent(request: ChatRequest):

    # .run() starts the loop:
    # 1. Ask Gemini -> 2. Gemini asks for Tool -> 3. Run Tool -> 4. Final Answer
    result = await agent.run(
        request.message,
        deps=request.user_id # Pass user_id into the RunContext
    )
    return result.output


class UserCityRequest(BaseModel):
    user_id: str
    city: str


@app.post("/askMeAnything")
async def ask_me_anything(request: UserCityRequest):
    config = {"configurable": {"thread_id": request.user_id}}
    user_input = f"I am user {request.user_id}. Suggest 3 restaurants in {request.city} based on my profile."

    try:
        result = agent_executor.invoke(
            {"messages": [("user", user_input)]},
            config=config
        )
        final_answer = result["messages"][-1].content

        print('lets put what we have in memeor', memory)

        return {
            "user_id": request.user_id,
            "recommendation": final_answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))