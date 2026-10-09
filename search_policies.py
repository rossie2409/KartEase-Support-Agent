


import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kartease_policies"


def search_policies(question):
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from .env")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001"),
        google_api_key=api_key,
    )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    results = vector_store.similarity_search(question, k=3)

    if not results:
        return "No relevant policy information was found."

    # Return the policy text to the AI instead of only printing it.
    formatted_results = []

    for document in results:
        source = document.metadata.get("source", "Unknown")
        formatted_results.append(
            f"Source: {source}\n{document.page_content}"
        )

    return "\n\n".join(formatted_results)


if __name__ == "__main__":
    question = input("Ask a KartEase policy question: ")
    print("\n" + search_policies(question))
