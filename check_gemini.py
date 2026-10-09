

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load settings from the .env file
load_dotenv()

# Create the Gemini model
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# Ask Gemini a simple question
response = llm.invoke("Say hello to a beginner learning AI.")

# Display the answer
print(response.content)
