
from dotenv import load_dotenv
from google import genai
import os

# Load API key from the root .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your root .env file."
    )

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Reply with exactly: NewsMind Gemini connection successful."
)

print(response.text)

