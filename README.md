# Explainable-Policy-Decision-Assistant_AI

Explainable-Policy-Decision-Assistant_AI is an AI-powered assistant for transparent, explainable policy decision-making. The project is built to help policymakers, regulators, and research teams evaluate policy options with clarity, auditability, and evidence-driven reasoning instead of relying on opaque black-box predictions.

The platform combines policy simulation, retrieval-augmented reasoning, and a modern user interface to make policy recommendations easier to understand, verify, and act on.

## Features

- Explainable policy reasoning that surfaces the steps behind each recommendation
- Policy simulation and scenario analysis for evaluating alternative outcomes
- Decision support workflows tailored for policy and governance teams
- Visualization tools that make audit trails, metrics, and results easy to interpret
- Integration readiness for connecting to datasets, external APIs, and knowledge bases

## Architecture

- FastAPI backend powering policy evaluation, ingestion, and audit logging
- React.js frontend built with Vite for a responsive dashboard experience
- Retrieval-augmented reasoning using Chroma vector search and Groq model inference
- Explainable model output with structured reasoning traces, evidence citations, and source references

## Prerequisites

- Python 3.11+ or compatible Python runtime
- Node.js 20+ and npm
- Git
- Access to a `GROQ_API_KEY` for model inference

## Installation

### Backend

```bash
git clone https://github.com/UniqCentro007/Explainable-Policy-Decision-Assistant_AI.git
cd Explainable-Policy-Decision-Assistant_AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create or update a `.env` file in the repository root with your Groq credentials and any database configuration required by `policy-assistant/app/main.py`.

### Frontend

```bash
cd policy-frontend
npm install
```

## Running locally

### Start the backend

From the repository root:

```bash
source .venv/bin/activate
uvicorn policy-assistant.app.main:app --host 0.0.0.0 --port 8080 --reload
```

Alternatively:

```bash
python policy-assistant/app/main.py
```

### Start the frontend

From `policy-frontend`:

```bash
npm run dev
```

Open the app in your browser at:

```text
http://localhost:5173
```

## Usage

1. Upload policy documents or datasets through the dashboard.
2. Configure policy parameters or submit a governance question.
3. Run policy simulations and review the explainable recommendation output.
4. Inspect audit trails, citation sources, and model confidence scores.
5. Use the history and admin views to track queries, metrics, and feedback.

## API Endpoints

- `POST /api/auth/login` — authenticate users and begin a session
- `POST /api/policy/evaluate` — submit a policy question and receive explainable output
- `POST /api/admin/upload-policy` — upload policy files for ingestion and vector indexing
- `GET /api/admin/metrics` — retrieve operational metrics and health indicators
- `GET /api/policy/history` — read the audit log of past policy evaluations
- `POST /api/policy/feedback` — submit clarity feedback for model recommendations

## Project Structure

```
Explainable-Policy-Decision-Assistant_AI/
├── README.md
├── requirements.txt
├── .env
├── policy-assistant/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── logic.py
│   │   ├── retrieval.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   ├── create_user.py
│   │   ├── populate_db.py
│   │   ├── reporting.py
│   │   └── training_data.py
│   ├── policies/
│   └── policy_vector_db/
├── policy-frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── README.md
│   ├── public/
│   └── src/
│       ├── api.js
│       ├── App.jsx
│       ├── main.jsx
│       ├── ArchitectureDiagram.jsx
│       └── components/
│           ├── AdminTab.jsx
│           ├── AuditTab.jsx
│           ├── HistoryTab.jsx
│           ├── LoginView.jsx
│           └── ThinkingState.jsx
```

## Docker Deployment

This repository does not include a container manifest by default, but the application is well suited for Docker deployment.

### Example docker-compose workflow

```yaml
version: '3.9'
services:
  backend:
    build: ./policy-assistant
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080
    ports:
      - '8080:8080'
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}

  frontend:
    build: ./policy-frontend
    command: npm run preview -- --host 0.0.0.0 --port 5173
    ports:
      - '5173:5173'
```

### Manual Docker build

```bash
docker build -t explainable-policy-backend ./policy-assistant
docker build -t explainable-policy-frontend ./policy-frontend
```

Then run the containers and map frontend and backend ports as needed.

## Contributing

Contributions are welcome from developers, policy experts, and researchers.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Add your changes with clear commit messages.
4. Push your branch and open a pull request against `main`.
5. Open an issue for large enhancements, integration requests, or architecture changes.

## License

This project is licensed under the MIT License. It is open source and free to use, modify, and distribute with attribution.

## Acknowledgments

Thanks to the AI and open-source communities for the tools and research that make explainable policy decision systems possible. This project is built on modern open-source infrastructure and aims to advance accountable AI for governance.
