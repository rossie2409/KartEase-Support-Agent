


import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# Find the project folder and load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Project paths and collection configuration
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kartease_policies"


def build_knowledge_base():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Check the .env file "
            "in your project folder."
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv(
            "GEMINI_EMBED_MODEL",
            "gemini-embedding-001",
        ),
        google_api_key=api_key,
    )

    # Reuse an existing collection to avoid unnecessary embeddings
    if DB_DIR.exists():
        try:
            existing_db = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=str(DB_DIR),
                embedding_function=embeddings,
            )

            count = existing_db._collection.count()

            if count > 0:
                print("Knowledge base already exists.")
                print(f"Stored policy chunks: {count}")

                # Verify that source metadata is present
                sample = existing_db._collection.get(
                    limit=min(count, 5),
                    include=["metadatas"],
                )

                metadatas = sample.get("metadatas") or []
                filenames_found = {
                    Path(metadata["source"]).name
                    for metadata in metadatas
                    if metadata and metadata.get("source")
                }

                if filenames_found:
                    print("Source filename metadata verified:")
                    for filename in sorted(filenames_found):
                        print(f"- {filename}")
                else:
                    print(
                        "Warning: source filenames were not found "
                        "in the sampled metadata."
                    )

                print("Reusing stored policy vectors.")
                return

        except Exception as exc:
            print(f"Could not reuse existing database: {exc}")

    # Load policy Markdown files
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

    # Split documents while preserving their source metadata
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    print(f"Loaded {len(documents)} policy documents.")
    print(f"Created {len(chunks)} text chunks.")

    # Save chunks and their metadata in Chroma
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
    )

    print(f"Saved {len(chunks)} chunks to Chroma.")
    print(f"Knowledge base location: {DB_DIR}")


if __name__ == "__main__":
    build_knowledge_base()

