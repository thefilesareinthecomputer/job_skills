import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables from .env file
load_dotenv()

# Retrieve the Perplexity AI API key from environment variables
api_key = os.getenv("PERPLEXITY_API_KEY")

# Validate the presence of the API key
if not api_key:
    raise ValueError("❌ PERPLEXITY_API_KEY not found in environment variables.")

# Configure the Perplexity LLM using CrewAI's LLM class
perplexity_llm = LLM(
    provider="perplexity",
    api_key=api_key,
    model="llama-3.1-sonar-large-128k-online",  # Specify the desired model
    base_url="https://api.perplexity.ai/",
    additional_kwargs={}  # Ensure no unsupported parameters are included
)

# Define the messages for the conversation
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What are the top 3 skills for AI engineers in 2025?"}
]

# Make the API request using the configured LLM
try:
    print("🔄 Sending request to Perplexity API...")
    response = perplexity_llm.completion(messages=messages)
    print("✅ API request successful!")
    print("\n--- Response Content ---")
    print(response)
except Exception as e:
    print(f"❌ An error occurred: {e}")