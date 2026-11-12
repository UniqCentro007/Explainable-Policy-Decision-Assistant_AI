# Explainable Policy Decision Assistant AI

A full-stack AI policy assistant for HR, compliance, and governance teams. The system combines retrieval-augmented generation (RAG), policy document ingestion, and human-in-the-loop review to answer employee and manager policy questions with grounded, explainable recommendations.

The repository includes:
- A FastAPI backend for policy evaluation, audit storage, user authentication, and admin metrics
- A React + Vite frontend for employee and manager workflows
- A ChromaDB vector store for company policy documents and clause-level retrieval
- A LangGraph-based reasoning loop with an auditor check before finalizing answers

## Overview

This project is designed to help organizations answer operational questions such as:
- Is a travel claim eligible under policy?
- What are the rules around data protection and employee privacy?
- What should an employee do when a policy exception is required?
- Which documents support the recommendation, and how confident is the answer?

Instead of responding from general knowledge alone, the assistant retrieves relevant passages from uploaded policy documents, reasons over them, and returns a structured answer with traceability.

## Key Features

- Policy-aware Q&A over uploaded PDFs and text files
- Multi-source retrieval across policy documents using ChromaDB and embeddings
- Explainable reasoning trace with evidence and source attribution
- Human approval and override flow for final recommendations
- User roles for employee and manager access
- Audit history and feedback collection for continuous review
- Admin dashboard for operational metrics and system status

## Architecture

- Backend: `policy-assistant/`
  - `app/main.py` exposes the FastAPI API and routes
  - `app/logic.py` contains the LangGraph agent and Groq-based reasoning flow
  - `app/retrieval.py` handles PDF/text ingestion and vector search
  - `app/database.py` defines the SQLite/PostgreSQL-backed schema
- Frontend: `policy-frontend/`
  - React app with login, audit, history, and admin screens
- Knowledge base: `policy-assistant/policies/` and `policy-assistant/policy_vector_db/`

## Repository Structure

```text
Policy Project/
├── README.md
├── requirements.txt
├── policy-assistant/
│   ├── app/
│   │   ├── create_user.py
│   │   ├── database.py
│   │   ├── logic.py
│   │   ├── main.py
│   │   ├── populate_db.py
│   │   ├── retrieval.py
│   │   └── schemas.py
│   ├── policies/
│   └── policy_vector_db/
├── policy-frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
└── .env (optional, local setup only)
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- A Groq API key for the model calls
- Access to policy PDFs or text files for ingestion

## Setup

### 1. Create a virtual environment

```bash
cd "c:\Users\Magesh\OneDrive\Documents\Policy Project"
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root or in the backend working directory, depending on your preferred setup.

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_CRITIC_MODEL=openai/gpt-oss-20b
DATABASE_URL=sqlite:///./policy_assistant.db
```

Notes:
- If `DATABASE_URL` is not set, the app falls back to a local SQLite database.
- The frontend defaults to `http://127.0.0.1:8080/api` unless `VITE_API_BASE_URL` is provided.

### 4. Create an initial user

The repo includes a helper for authorizing users.

```bash
cd policy-assistant
python app/create_user.py
```

Update the script with your preferred usernames and passwords before running it in a real environment.

### 5. Ingest policy documents

Place policy files in `policy-assistant/policies/` and then run:

```bash
cd policy-assistant
python app/populate_db.py
```

This indexes the documents into ChromaDB for retrieval by the policy reasoning engine.

## Running the Application

### Start the backend

```bash
cd policy-assistant
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

### Start the frontend

```bash
cd policy-frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal, typically `http://localhost:5173`.

## Supported Workflows

### Employee workflow
- Login to the assistant
- Ask a policy question in natural language
- Review the recommendation, source-backed reasoning, and confidence score
- Submit feedback about clarity or usefulness

### Manager workflow
- View operational metrics and audit summaries
- Review system health and policy evaluation trends
- Approve or override decisions when needed

## Notes

- Policy answers are grounded in the uploaded documents for the configured knowledge base.
- The assistant is designed for explainability; it shows the reasoning flow and evidence used in generating the answer.
- The system is intended to support governance and policy review, not to replace formal legal or HR approval processes.

## License

This project is provided as-is for internal or educational use unless the repository owner specifies a different license.
