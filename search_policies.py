

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Find the project folder and load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Project configuration
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kartease_policies"

# Initial relevance threshold; validate it with test questions
RELEVANCE_THRESHOLD = 0.45


def search_policies(question):
    """Search KartEase policy documents and return relevant sources."""

    question = question.strip()

    if not question:
        return "Please enter a policy question."

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing from the .env file."
        )

    # Check whether the policy knowledge base exists
    if not DB_DIR.exists():
        return (
            "The policy knowledge base has not been created yet. "
            "Please run python ingest_policies.py first."
        )

    # Configure embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv(
            "GEMINI_EMBED_MODEL",
            "gemini-embedding-001",
        ),
        google_api_key=api_key,
    )

    # Connect to the existing Chroma database
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    # Retrieve documents along with relevance scores
    results = vector_store.similarity_search_with_relevance_scores(
        question,
        k=3,
    )

    if not results:
        return (
            "Sorry, I couldn't find relevant information in "
            "the KartEase policies for that question."
        )

    # Keep only results above the initial relevance threshold
    relevant_results = [
        (document, score)
        for document, score in results
        if score >= RELEVANCE_THRESHOLD
    ]

    if not relevant_results:
        return (
            "Sorry, I couldn't find relevant information in "
            "the KartEase policies for that question. "
            "Please ask about returns, refunds, shipping, "
            "payments, or warranties."
        )

    # Include source filenames so the agent can cite its sources
    formatted_results = []

    for document, score in relevant_results:
        source = document.metadata.get("source", "Unknown")
        source_name = Path(source).name if source != "Unknown" else source

        formatted_results.append(
            f"Source: {source_name}\n"
            f"Policy information:\n{document.page_content}"
        )

    return "\n\n---\n\n".join(formatted_results)


if __name__ == "__main__":
    question = input("Ask a KartEase policy question: ")
    print("\n" + search_policies(question))
