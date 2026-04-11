# 🦋 TwinlyAI Backend API

FastAPI-powered backend for **TwinlyAI**, an AI-driven platform that empowers candidates to create "Digital Twins" and allows recruiters to intelligently discover talent through semantic search and interactive AI personas.

## 🚀 Core Features

- **Digital Twin Orchestration**: Manage AI personas for candidates, including summary generation, skill extraction, and social link integration.
- **AI Agent Pipline (LangGraph)**: Multi-step AI workflows for indexing candidate data, processing resumes, and orchestrating recruiter-to-twin conversations.
- **Semantic Talent Discovery**: Advanced candidate search using vector embeddings (Qdrant) and RAG (Retrieval-Augmented Generation) with Groq LLMs.
- **Asynchronous Processing**: Background jobs for GitHub indexing and heavy AI tasks using **Celery** and **Redis**.
- **Voice Capabilities**: Real-time Text-to-Speech (TTS) using **Edge-TTS** for interactive AI profiles.
- **Universal Auth**: Secure email/password authentication alongside Google and GitHub OAuth flows.
- **Workflow Tracking**: Integrated state management for candidate and recruiter onboarding sequences.

## 🛠️ Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Agent/RAG**: [LangGraph](https://www.langchain.com/langgraph), [LangChain](https://www.langchain.com/), [Groq](https://groq.com/)
- **Database**: [MongoDB](https://www.mongodb.com/) (Motor/AsyncIO)
- **Vector Search**: [Qdrant](https://qdrant.tech/)
- **Background Jobs**: [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/)
- **Voice/TTS**: [Edge-TTS](https://github.com/rany2/edge-tts)
- **Deployment**: [AWS App Runner](apprunner.yaml), [Render](render.yaml)

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Docker Desktop (for local services)

### 2. Services Configuration (Docker)
Start the essential services (MongoDB, Redis, Qdrant) using Docker Compose:
```bash
docker-compose up -d
```

### 3. Environment Configuration
Create a `.env` file based on the template below:
```env
MONGO_CONNECTION_STRING=mongodb://localhost:27017/twinlyai_db
MONGO_DB_NAME=twinlyai_db
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=fernet-encryption-key
GROQ_API_KEY=your-groq-key
GITHUB_CLIENT_ID=your-id
GITHUB_CLIENT_SECRET=your-secret
CELERY_BROKER_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
FRONTEND_URL=http://localhost:3000
```

### 4. Application Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000

# Start the Celery Worker (In a separate terminal)
celery -A app.worker.tasks worker --loglevel=info
```

## 📂 Project Structure

- `app/api/v1/`: API endpoints (auth, connectors, recruiter, etc.)
- `app/worker/`: Celery task definitions and background logic.
- `app/core/`: Security, config, and LangGraph agent logic.
- `app/services/`: Business logic for external service integrations (GitHub, LinkedIn).
- `scripts/`: Utility scripts for database inspection and testing.

## 🧪 Utility Scripts
- `inspect_db.py`: Quick tool to view MongoDB collections and data.
- `test_onboarding.py`: Scenario-based testing for onboarding flows.

## 📄 License
This project is proprietary. © 2025 TwinlyAI.
