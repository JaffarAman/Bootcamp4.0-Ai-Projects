import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_assignment(prompt):
    structured_prompt = f"""
    You are an expert teacher.

    Create a detailed assignment with the following structure:

    Title:
    Description:
    Objectives:
    Requirements:
    Tasks (step by step):
    Submission Instructions:
    Evaluation Criteria:

    Topic: {prompt}

    Make it beginner-friendly and well formatted.
    """

    response = model.generate_content(structured_prompt)
    return response.text