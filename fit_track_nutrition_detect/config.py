from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")