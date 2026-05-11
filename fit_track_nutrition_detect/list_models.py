import requests
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini models endpoint
url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

# Call API
response = requests.get(url)

# Convert response to JSON
data = response.json()

# Print models nicely
if "models" in data:
    print("\n✅ Available Gemini Models:\n")
    for model in data["models"]:
        print("Model Name:", model["name"])
        print("Supported Methods:", model.get("supportedGenerationMethods", []))
        print("-" * 50)
else:
    print("❌ Error fetching models:")
    print(data)