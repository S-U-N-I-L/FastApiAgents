import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")



# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

# 2. Initialize the client (it automatically looks for OPENAI_API_KEY in env)
client = OpenAI(api_key=apikey)

# 3. Simple Chat Call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "where is biaora"}
    ],
    temperature=0.7
)

# 4. Print the result
# print(response.choices[0].message.content)


client = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=apikey)
messages = [AIMessage("you said you want top cities in india", name="Model")]
messages.append(HumanMessage("yes thats right", name="sunil"))
messages.append(AIMessage("ok here is the list ", name="Model"))
print(client.invoke(messages))


