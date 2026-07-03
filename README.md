# Calmindra - Premium Mental Health Companion with Cloud GraphRAG

Calmindra is a production-ready mental health companion utilizing modern AI architectures: **Graph Retrieval-Augmented Generation (GraphRAG)**. The application couples a Next.js frontend, a FastAPI backend, Google Vertex AI models, and Neo4j database graph persistence.

---

## 🚀 Architecture

```
Frontend (Next.js)      Backend (FastAPI)     AI Engine (Vertex AI)
      ↓                        ↓                      ↓
   Port 3000   ←──→  HTTP  ←──→ Port 8000   ←──→   Gemini-1.5-Flash
      ↓                        ↓                      ↓
Thread List Sidebar       Neo4j AuraDB       Semantic Vector Embeddings
 (Zustand State)        (Graph History)         (text-embedding-004)
```

---

## 🌟 Key Features

### Frontend (Next.js + TypeScript)
- **Multi-Thread Sidebar**: Dynamic thread list sidebar for conversation CRUD matching state persistence.
- **Real-Time Interface**: Chat layout designed with `@assistant-ui/react` featuring custom loading animations and premium styling.
- **Type-Safe Adapters**: Implements `RemoteThreadListAdapter` and custom `ThreadHistoryAdapter` to load historic messages from the backend API.

### Backend (FastAPI + Python)
- **GraphRAG Engine**: Retrieves semantically similar therapeutic documents in Neo4j vector space to enrich the system instructions context sent to Gemini.
- **Chronological Graph Trees**: Saves conversations linked sequentially in the graph:
  `(:Thread)-[:HAS_MESSAGE]->(:Message)-[:NEXT_MESSAGE]->(:Message)`
- **Google GenAI Integration**: Utilizes unified Google `google-genai` SDK for low-latency embeddings and chat completions.
- **Mock Testing Suite**: Standardized `pytest` unit test fixtures mocking external database and model clients for testing.

---

## 📂 Project Structure

```
calmindra/
├── frontend/                  # Next.js React application
│   ├── app/                   # App Router pages and API proxy routes
│   ├── components/            # Reusable UI component modules
│   └── hooks/                 # Custom React hooks (thread and history managers)
├── backend/                   # FastAPI Python application
│   ├── app/
│   │   ├── routes/            # API endpoints (chat, threads)
│   │   ├── services/          # Services (Neo4jClient, VertexClient)
│   │   └── scripts/           # DB Seeding & RAG scripts
│   ├── tests/                 # Pytest unit suites
│   ├── Dockerfile             # Backend container definition
│   └── requirements.txt       # Backend dependencies
├── .github/workflows/         # GitHub Actions CI/CD workflows
├── docker-compose.yml         # Container orchestrations
└── start.sh                   # Dev environment bootstrapper
```

---

## 🛠️ Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)

### Environment Setup
Create a `backend/.env` file in the `backend/` directory referencing `backend/.env.example`:
```bash
NEO4J_URI=neo4j+s://<your-aura-db-uri>
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-password>
GEMINI_API_KEY=<your-gemini-api-key>
REDIS_URL=redis://localhost:6379  # optional fallback URL
```

### Run Locally
```bash
# Launch backend in docker container and start frontend server
./start.sh
```

---

## 🧪 Verification & Development

### Run Backend Tests
Ensure your python dependencies and `pytest` are installed locally, then run:
```bash
cd backend
python3 -m pytest tests/
```

### GitHub Actions CI/CD
A GitHub Actions runner is configured under `.github/workflows/ci-cd.yml` to trigger on pull requests and pushes to `main`:
1. Executes backend mock testing suite with `pytest`.
2. Validates frontend TypeScript compilation and Next.js production builds.
3. Tests Dockerizing the backend codebase.

---

## 🔒 License
This project is licensed under the MIT License.
