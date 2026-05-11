from google import genai

from config import GEMINI_API_KEY

# API key correct way
client = genai.Client(api_key=GEMINI_API_KEY)

models = client.models.list()

print("\n🔥 Available Gemini Models:\n")

for model in models:
    print(model.name)