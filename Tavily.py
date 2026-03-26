import os

from dotenv import load_dotenv
from tavily import TavilyClient

# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")



# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
api_key = os.getenv("TAVILY_API_KEY")

# Initialize with your API key
tavily = TavilyClient(api_key=api_key)

# Execute a search
response = tavily.search("where is biaora get some image")
res = tavily.crawl("https://sunilkumarsharma.com.np/")

print(res)

# Print the results
print(response)
for result in response['results']:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content']}\n")
