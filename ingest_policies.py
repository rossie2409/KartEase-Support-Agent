

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# Find the project folder and load the API key
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Project paths
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kartease_policies"


def build_knowledge_base():
    # Check whether the API key is available
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Check the .env file "
            "in your project folder."
        )

    # Configure the embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv(
            "GEMINI_EMBED_MODEL",
            "gemini-embedding-001",
        ),
        google_api_key=api_key,
    )

    # Load existing vectors if the database already contains data
    if DB_DIR.exists():
        try:
            existing_db = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=str(DB_DIR),
                embedding_function=embeddings,
            )

            if existing_db._collection.count() > 0:
                print("Knowledge base already exists.")
                print("Reusing stored policy vectors.")
                return

        except Exception as exc:
            print(f"Could not reuse existing database: {exc}")

    # Load policy documents
    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()

    if not documents:
        raise ValueError(
            f"No Markdown policy documents found in {DATA_DIR}"
        )

    # Split documents into smaller chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    print(f"Loaded {len(documents)} policy documents.")
    print(f"Created {len(chunks)} text chunks.")

    # Store the chunks in Chroma
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
    )

    print(f"Saved {len(chunks)} chunks to Chroma.")
    print(f"Knowledge base location: {DB_DIR}")


if __name__ == "__main__":
    build_knowledge_base()
