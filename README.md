
# KartEase – AI-Powered Customer Support Agent

## 1. Project Overview

KartEase is an AI-powered customer support assistant that helps customers get answers to product policies and order-related questions.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from company policy documents and uses an order lookup tool to retrieve order details from a CSV file.

## 2. Objectives

- Answer customer questions about returns, refunds, shipping, payments, and warranties.
- Retrieve relevant information from policy documents.
- Look up order details using an order ID.
- Handle invalid order IDs without inventing order information.
- Provide clear, concise responses through a conversational interface.

## 3. Technologies Used

- Python
- Google Gemini API
- LangChain
- ChromaDB
- Google Generative AI Embeddings
- CSV for order data
- Pytest for automated testing
- python-dotenv for environment configuration

## 4. System Features

### Policy Search Using RAG

The policy documents are loaded, split into smaller text chunks, and converted into vector embeddings. ChromaDB stores these vectors.

When a customer asks a policy question, the system retrieves relevant text chunks using similarity search. Gemini uses the retrieved information to formulate an answer.

### Order Lookup

The order lookup tool searches `orders.csv` using the provided order ID.

It returns the matching order details or reports when no matching order is found.

### Conversational Support

The Gemini model decides when to use the policy search or order lookup tool and presents the result in a readable format.

## 5. Project Structure

```text
kartease_starter/
├── data/
│   ├── payments_and_offers.md
│   ├── returns_and_refunds.md
│   ├── shipping_and_delivery.md
│   └── warranty_and_repairs.md
├── chroma_db/
├── tests/
│   ├── test_order_tools.py
│   └── test_search_policies.py
├── .env
├── .gitignore
├── ingest_policies.py
├── search_policies.py
├── order_tools.py
├── support_agent.py
├── orders.csv
├── requirements-langchain.txt
├── pytest.ini
└── README.md
```

The `.env` file contains local configuration and should not be committed to GitHub. The `chroma_db/` directory stores the persistent policy vector database.

## 6. Prerequisites

- Python 3.11 or a compatible Python version
- A Google Gemini API key
- Internet connectivity for Gemini API calls
- Required Python packages

The project was tested using Python 3.13.15.

## 7. Installation and Setup

### Step 1: Create and activate a virtual environment

On Windows CMD, run:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements-langchain.txt
```

### Step 3: Configure environment variables

Create a `.env` file in the project root:

```text
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EMBED_MODEL=gemini-embedding-001
```

Replace `your_google_api_key` with your own API key. Never commit your real API key to GitHub.

### Step 4: Build the policy knowledge base

```bash
python ingest_policies.py
```

This loads the policy Markdown files, creates text chunks, generates embeddings, and stores them in ChromaDB. The existing knowledge base is reused when available, avoiding unnecessary re-embedding on subsequent runs.

### Step 5: Start the support agent

```bash
python support_agent.py
```

Ask a question about policies or provide an order ID.

Type `exit` to close the application.

## 8. Example Questions

### Policy Questions

- What is the return window for electronics?
- How long does standard shipping take?
- What are the warranty conditions?
- What payment methods does KartEase accept?
-