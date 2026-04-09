import os

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


# 1. Determine the environment (default to 'local')
env = os.getenv("APP_ENV", "local")

# Load variables from .env into the environment
load_dotenv(f".env.{env}")

# Now you can access them using os.getenv
apikey = os.getenv("OPENAI_API_KEY")

# 1. THE DATA: Your "Long-Term Memory" source
raw_text = "The secret code for the vault is 8802. The office is located on the 4th floor. i am sunil i live in moline, i have audi a4"

# 2. CHUNKING: Break text into smaller pieces so they fit in the AI's 'view'
# We use RecursiveCharacterTextSplitter as it's the recommended default.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,      # Max characters per chunk
    chunk_overlap=20     # Keeps some context between chunks
)
chunks = text_splitter.split_text(raw_text)

# 3. EMBEDDING & STORAGE: Turn text into numbers and save to a DB
# We'll use Chroma as a simple local vector database.
vector_db = Chroma.from_texts(
    texts=chunks,
    embedding=OpenAIEmbeddings(), # Converts text to vectors
    persist_directory="./my_ai_memory" # Saves it to your hard drive
)

# 4. RETRIEVAL: Finding the right 'memory'
query = "tell me car of sunil"
relevant_docs = vector_db.similarity_search(query)

print(relevant_docs[0].page_content)
# Output: "The office is located on the 4th floor."
