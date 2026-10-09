

# KartEase – AI-Powered Customer Support Agent

## 1. Project Overview

KartEase is an AI-powered customer support assistant that helps customers get answers to product policy and order-related questions.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from company policy documents and an order lookup tool to retrieve order details from a CSV file.

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

The policy documents are loaded, split into smaller text chunks, and converted into vector embeddings. ChromaDB stores these vectors persistently.

When a customer asks a policy question, the system retrieves relevant text chunks using similarity search. The language model uses the retrieved information to formulate an answer.

Policy results include source filenames to help identify the supporting documents.

### Order Lookup

The order lookup tool searches `orders.csv` using the provided order ID.

The `get_order_status(order_id)` function returns matching order details or a clear message when an order ID does not exist. The existing `lookup_order()` function is retained for compatibility.

### Conversational Support

The Gemini model chooses the policy search tool, order lookup tool, or both depending on the customer's question.

The terminal chat displays which tool is being used and continues until the user types `exit`.

### Handling Unrelated Questions

The agent is instructed to help only with KartEase orders and policies. It should not answer unrelated questions using general knowledge.

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

The `.env` file stores local configuration and API credentials and must not be committed to GitHub.

The `chroma_db/` directory stores the persistent policy vector database.

## 6. Prerequisites

- Python 3.11 or a compatible Python version
- Google Gemini API key
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

Replace `your_google_api_key` with your own API key. Never commit the real API key to GitHub.

### Step 4: Build the policy knowledge base

```bash
python ingest_policies.py
```

This loads the policy Markdown files, creates text chunks, generates embeddings, and stores them in ChromaDB.

When the existing knowledge base is available, the ingestion script reuses the stored vectors instead of embedding all documents again.

### Step 5: Start the support agent

```bash
python support_agent.py
```

Ask questions about policies or provide an order ID.

Type `exit` to close the application.

## 8. Example Questions

### Policy Questions

- What is the return window for electronics?
- Can I return earbuds if they are not defective?
- What is the delivery charge on a ₹350 order?
- If I order at 4 PM, when will it be dispatched?
- Can I use a coupon together with a bank offer?
- How long is Extended Protection, and when can I buy it?
- What payment methods does KartEase accept?
- How long does a refund take after returning a product?

### Order Questions

- What is the status of order KE1001?
- Where is my order KE1002?
- What is the status of order ke1005?
- What is the status of order KE9999?

### Combined Questions

- What is the status of order KE1002, and how long does standard shipping take for non-metro locations?
- My return for KE1006 was picked up. When will I get my refund?

### Unrelated Questions

- What is the capital of France?
- Who is the CEO of Google?
- Write a poem about Diwali.

The expected behavior for unrelated questions is a polite refusal indicating that the assistant can only help with KartEase orders and policies.

## 9. Automated Test Results

Run the automated tests from the project directory:

```bash
python -m pytest -v
```

**Latest observed result: 5 tests passed.**

The automated tests cover:

- Existing order lookup
- Unknown order lookup
- Case-insensitive order IDs
- Return policy search
- Shipping policy search

These tests do not require a Gemini call for the order lookup tests.

## 10. Agent Evaluation — 14 Required Questions

The table below records known results from the development and demonstration sessions. Questions not verified against their exact evaluation case are marked accordingly.

| # | Evaluation question | Expected result | Status |
|---|---|---|---|
| 1 | How many days do I have to return a phone? | 10 days from delivery | Pass — verified |
| 2 | Can I return earbuds if I just don't like them? | Not returnable unless damaged or defective | Not verified |
| 3 | What is the delivery charge on a ₹350 order? | ₹40 delivery charge | Not verified |
| 4 | If I order at 4 PM, when will it be dispatched? | Next working day | Not verified |
| 5 | Can I use a coupon together with a bank offer? | No | Not verified |
| 6 | How long is Extended Protection and when can I buy it? | One extra year; purchase within 30 days of delivery | Not verified |
| 7 | Can I pay cash on delivery for a ₹12,000 order? | No; COD limit is ₹10,000 | Not verified |
| 8 | Where is my order KE1002? | Shipped; expected date 2026-10-07 | Pass — order and date verified |
| 9 | What is the status of order ke1005? | Processing; expected date 2026-10-08 | Not verified |
| 10 | What is the status of order KE9999? | Friendly unknown-order message | Pass — verified |
| 11 | My return for KE1006 was picked up. When will I get my refund? | Quality check followed by refund in 5–7 working days | Not verified |
| 12 | I paid cash for KE1009. If I return it, how do I get my money back? | Refund to bank account or UPI | Not verified |
| 13 | Who is the CEO of Google? | Required KartEase-only refusal | Pass — unrelated-question refusal demonstrated |
| 14 | Write me a poem about Diwali. | Required KartEase-only refusal | Not verified |

### Improvement Attempted

- Added source filenames to policy search results.
- Updated the policy search fallback message to the required wording when no relevant policy chunks are found.
- Added `get_order_status(order_id)` while preserving `lookup_order()` compatibility.
- Added terminal output identifying the selected tool.
- Reran the automated tests and confirmed five tests passed.

### Known Limitations

- Some evaluation questions still require verification against their exact expected answers.
- Similarity thresholds alone cannot guarantee that every unrelated question will trigger the fallback.
- The agent does not automatically flag an expected delivery date that has already passed.
- The current order data is a sample CSV rather than a live order management system.

## 11. Three-Minute Demo Plan

### 0:00–0:30 — Introduction

Introduce KartEase and explain that it combines RAG-based policy search with order lookup.

### 0:30–1:00 — Policy Search

Ask:

`What is the return window for electronics?`

Explain how the system retrieves policy information and includes source filenames.

### 1:00–1:30 — Order Lookup

Ask:

`What is the status of order KE1001?`

Then ask:

`What is the status of order KE9999?`

Demonstrate valid-order retrieval and friendly handling of an unknown order.

### 1:30–2:00 — Combined Tools

Ask:

`What is the status of order KE1002, and how long does standard shipping take for non-metro locations?`

Explain that the agent can use both order lookup and policy search in one request.

### 2:00–2:30 — Unrelated Question

Ask:

`What is photosynthesis?`

Demonstrate the KartEase-only refusal.

### 2:30–3:00 — Architecture and Testing

Show the policy documents, persistent Chroma database, order CSV, and the five passing automated tests.

## 12. Conclusion

KartEase demonstrates an AI-powered customer support workflow using retrieval-augmented generation, a persistent vector database, and tool-based order lookup.

The prototype provides policy assistance, retrieves order information, and handles unknown orders and unrelated questions. Further evaluation and improvements are needed before production deployment.
