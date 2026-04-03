# 🦋 TwinlyAI Backend API

FastAPI-powered backend for **TwinlyAI**, an AI-driven platform that empowers candidates to create "Digital Twins" and allows recruiters to intelligently discover talent through semantic search.

## 🚀 Core Features

- **Digital Twin Orchestration**: Manage AI personas for candidates, including summary generation, skill extraction, and social link integration.
- **Semantic Talent Discovery**: Advanced candidate search using vector embeddings (Qdrant) and RAG (Retrieval-Augmented Generation) with Groq LLMs.
- **Recruiter Dashboard API**: Endpoints for candidate listing, detailed profile viewing, and real-time AI-to-Recruiter chat streaming.
- **Universal Auth & OAuth**: Secure email/password authentication alongside Google and GitHub third-party login flows.
- **Workflow & Onboarding Tracking**: Integrated state management to ensure users complete their respective onboarding processes.

## 🛠️ Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [MongoDB](https://www.mongodb.com/) (Motor/AsyncIO)
- **Vector Search**: [Qdrant](https://qdrant.tech/)
- **AI/LLM**: [Groq](https://groq.com/) & [HuggingFace](https://huggingface.co/)
- **Background Jobs**: [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/)
- **Auth**: JWT (Jose) + [Authlib](https://docs.authlib.org/)

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- MongoDB (Local or Atlas)
- Redis (for Celery)
- Qdrant (Local or Cloud)

### 2. Environment Configuration
Create a `.env` file in the root directory based on the following template:

```env
# Database
MONGO_CONNECTION_STRING=mongodb://localhost:27017/twinlyai_db
MONGO_DB_NAME=twinlyai_db

# Security
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=fernet-encryption-key

# AI Services
GROQ_API_KEY=your-groq-key
HUGGINGFACE_API_KEY=your-hf-token

# OAuth
GITHUB_CLIENT_ID=your-id
GITHUB_CLIENT_SECRET=your-secret
GOOGLE_CLIENT_ID=your-id
GOOGLE_CLIENT_SECRET=your-secret

# Vector DB
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key

# URLs
FRONTEND_URL=http://localhost:3000
ENV=dev
```

### 3. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

## 📂 Project Structure

- `app/api/v1/`: API endpoints (auth, bots, recruiter, users, etc.)
- `app/core/`: Security, config, and RAG pipeline logic.
- `app/db/`: Database session management.
- `app/schemas/`: Pydantic models for request/response validation.
- `app/services/`: Business logic and external service integrations.

## 📄 License
This project is proprietary. © 2025 TwinlyAI.
