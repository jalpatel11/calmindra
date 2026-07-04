# Calmindra - Deployed GraphRAG Mental Health Backend

Calmindra is a production-ready mental health chatbot backend using **Graph Retrieval-Augmented Generation (GraphRAG)**. This repository houses the FastAPI backend, Neo4j database integration, and Google Vertex AI model wrappers.

The Next.js frontend has been decoupled and is hosted in a separate repository: **[Calmindra-Frontend](https://github.com/jalpatel11/Calmindra-Frontend)**.

---

## 🚀 Architecture

```
Backend (FastAPI)       AI Engine (Vertex AI)
      ↓                        ↓
  Port 8000           ←──→ Gemini-1.5-Flash
      ↓                        ↓
 Neo4j AuraDB         Semantic Vector Embeddings
(Graph History)          (text-embedding-004)
```

---

## 🌟 Key Features

- **GraphRAG Engine**: Performs semantic vector searches on therapeutic document nodes in Neo4j AuraDB to enrich completions context.
- **Chronological Session Logging**: Saves conversation trees in Neo4j linked sequentially per thread:
  `(:Thread)-[:HAS_MESSAGE]->(:Message)-[:NEXT_MESSAGE]->(:Message)`
- **Google GenAI SDK**: Uses the unified `google-genai` package for completions and embeddings.
- **Testing Architecture**: Complete pytest mock environment validating routes and database handlers without requiring live cloud services.

---

## 📂 Project Structure

```
calmindra/
├── backend/                   # FastAPI Python application
│   ├── app/
│   │   ├── routes/            # API endpoints (chat, threads)
│   │   ├── services/          # Clients (Neo4jClient, VertexClient)
│   │   └── scripts/           # DB Seeding & GraphRAG scripts
│   ├── tests/                 # Pytest unit suites
│   ├── Dockerfile             # Backend container definition
│   └── requirements.txt       # Backend dependencies
├── .github/workflows/         # GitHub Actions CI/CD workflows
├── docker-compose.yml         # Container configurations
└── start.sh                   # Dev environment launcher
```

---

## 🛠️ Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.10+

### Environment Setup
Create a `backend/.env` file in the `backend/` directory referencing `backend/.env.example`:
```bash
NEO4J_URI=neo4j+s://<your-auradb-id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
GEMINI_API_KEY=<your-gemini-api-key>
REDIS_URL=redis://localhost:6379  # optional fallback URL
```

### Run Locally
```bash
# Launch backend service in local docker container
./start.sh
```

---

## 🧪 Verification & Development

### Run Pytest Suite
Ensure your python dependencies and `pytest` are installed locally, then run:
```bash
cd backend
python3 -m pytest tests/
```

### GitHub Actions CI/CD
A GitHub Actions runner is configured under `.github/workflows/ci-cd.yml` to trigger on pull requests and pushes to `main`:
1. Executes backend mock testing suite with `pytest`.
2. Tests Dockerizing the backend codebase.

---

## 🔒 License
This project is licensed under the MIT License.
