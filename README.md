<div align="center">
  <h1>🦋 TwinlyAI Backend API</h1>
  <p><strong>The Intelligence & Orchestration Engine for TwinlyAI</strong></p>

  [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
  [![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com/)
  [![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)
</div>

<br />

The **TwinlyAI Backend** is a highly asynchronous, FastAPI-powered engine. It serves as the central nervous system for the TwinlyAI platform, orchestrating AI workflows via LangGraph, managing vector embeddings, and powering real-time conversational agents.

---

## 🚀 Core Capabilities

- **Digital Twin Orchestration**: Manage AI personas for candidates, including summary generation, skill extraction, and social link integration.
- **AI Agent Pipelines (LangGraph)**: Multi-step AI workflows for indexing candidate data, processing resumes, and orchestrating recruiter-to-twin conversations.
- **Semantic Talent Discovery**: Advanced candidate search using vector embeddings (**Qdrant**) and RAG (Retrieval-Augmented Generation) powered by **Groq** LLMs.
- **Real-Time Voice Infrastructure**: Integrated with **LiveKit** to deploy low-latency, WebRTC-based AI voice agents capable of VAD, interruption handling, and streaming TTS.
- **Asynchronous Processing**: Robust background jobs for GitHub indexing and heavy AI tasks utilizing **Celery** and **Redis**.
- **Universal Auth**: Secure JWT email/password authentication alongside Google and GitHub OAuth flows.

---

## 🛠️ Technology Stack

| Category | Technology |
| --- | --- |
| **API Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python) |
| **AI / RAG Logic** | [LangGraph](https://www.langchain.com/langgraph), [LangChain](https://www.langchain.com/), [Groq](https://groq.com/) |
| **Database** | [MongoDB](https://www.mongodb.com/) (Motor/AsyncIO) |
| **Vector Search** | [Qdrant](https://qdrant.tech/) |
| **Task Queue** | [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/) |
| **Voice / RTC** | [LiveKit Server SDK](https://livekit.io/) & `livekit-agents`, [Piper TTS](https://github.com/rhasspy/piper) |
| **Deployment** | Docker, Hugging Face Spaces, AWS App Runner |

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose (for local auxiliary services)

### 2. Infrastructure Services (Docker)
Start the essential data stores (MongoDB, Redis, Qdrant) and the LiveKit Media Server:
```bash
docker-compose up -d
```

### 3. Environment Configuration
Create a `.env` file in the root backend directory:
```env
# Database & Cache
MONGO_CONNECTION_STRING=mongodb://localhost:27017/twinlyai_db
MONGO_DB_NAME=twinlyai_db
CELERY_BROKER_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# Security
SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=fernet-encryption-key

# AI & External APIs
GROQ_API_KEY=your-groq-key
GITHUB_CLIENT_ID=your-github-id
GITHUB_CLIENT_SECRET=your-github-secret

# LiveKit WebRTC
LIVEKIT_URL=http://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

FRONTEND_URL=http://localhost:3000
```

### 4. Application Setup
```bash
# Install all required Python dependencies
pip install -r requirements.txt

# Start the primary FastAPI HTTP server
uvicorn app.main:app --reload --port 8000

# Start the Celery Worker (In a separate terminal)
celery -A app.worker.tasks worker --loglevel=info

# Start the LiveKit Voice Agent Worker (In a separate terminal)
python -m app.worker.livekit_agent
```

---

## 📂 Project Architecture

```text
backend/
├── app/
│   ├── api/v1/        # API route handlers (auth, recruiter endpoints, token dispensers)
│   ├── core/          # Core configurations, security middleware, and LangGraph pipelines
│   ├── services/      # Business logic and external API integrations (GitHub, LinkedIn)
│   └── worker/        # Celery tasks and LiveKit Voice Agent worker processes
├── scripts/           # Standalone utility scripts (DB inspection, onboarding tests)
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container definition (Supervisord managed)
└── docker-compose.yml # Local infrastructure stack
```

---

## 📄 License
This project is proprietary. © 2026 TwinlyAI. All rights reserved.
