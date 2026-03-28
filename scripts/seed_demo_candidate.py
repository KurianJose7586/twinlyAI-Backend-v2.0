"""
TwinlyAI — Demo Candidate Seeder (50 Candidates)
==================================================
Clears all existing bot records and seeds the database with 50 realistic,
diverse, high-quality candidate profiles across multiple tech disciplines.

Run from the backend root directory:
    python scripts/seed_demo_candidates.py

Requirements:
    - .env file present in the backend root (with MONGO, QDRANT, GROQ keys)
    - pip install reportlab (already in requirements.txt)
"""

import os
import sys
import asyncio
from pathlib import Path
from bson import ObjectId

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.core.rag_pipeline import RAGPipeline, GlobalRecruiterIndex
from app.db.session import bots_collection, users_collection

# ──────────────────────────────────────────────────────────────────────────────
# 50 HIGH-QUALITY CANDIDATES
# ──────────────────────────────────────────────────────────────────────────────

CANDIDATES = [

    # ── FRONTEND (10) ──────────────────────────────────────────────────────────

    {
        "name": "Priya Sharma",
        "summary": "Frontend engineer with 3 years building performant React and Next.js applications. Specialises in design systems, accessibility, and Tailwind-based UI libraries. Previously at Razorpay, shipped the merchant onboarding redesign used by 200k+ businesses.",
        "skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "Figma", "GraphQL", "Storybook", "Vitest"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/priya-sharma-frontend",
        "github_url": "https://github.com/priya-sharma-dev",
        "website_url": "https://priyasharma.dev",
        "projects": [
            {"name": "Merchant Dashboard Redesign", "description": "Led UI overhaul for Razorpay merchant portal using React 18 and design tokens. Reduced load time by 40%.", "link": ""},
            {"name": "react-aria-kit", "description": "Open-source accessible component library with 800+ GitHub stars, built on React Aria primitives.", "link": "https://github.com/priya-sharma-dev/aria-kit"},
        ],
    },
    {
        "name": "Kavya Reddy",
        "summary": "Frontend developer with 2 years experience in React and Vue.js, with a strong focus on performance optimisation and Core Web Vitals. Reduced LCP by 60% at an ed-tech startup through bundle splitting and image lazy-loading. Great eye for UI/UX details.",
        "skills": ["React", "Vue.js", "JavaScript", "Vite", "Pinia", "CSS Animations", "Webpack", "Lighthouse"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/kavya-reddy-frontend",
        "github_url": "https://github.com/kavya-ui",
        "website_url": "https://kavyareddy.dev",
        "projects": [
            {"name": "EduPlatform Performance Overhaul", "description": "Vue.js bundle split + lazy loading strategy that improved LCP from 8s to 3.2s on 3G connections.", "link": ""},
            {"name": "vue-motion-kit", "description": "Lightweight Vue 3 animation composables library inspired by Framer Motion. 200+ npm downloads/week.", "link": "https://github.com/kavya-ui/vue-motion-kit"},
        ],
    },
    {
        "name": "Harsh Agarwal",
        "summary": "Senior frontend engineer with 5 years at product companies. Deep React expertise with a focus on micro-frontend architectures and module federation. At Nykaa, led the migration from a monolithic React app to a micro-frontend setup, reducing per-team deployment conflicts by 80%.",
        "skills": ["React", "Module Federation", "Webpack", "TypeScript", "Cypress", "Redux", "React Query", "Jest"],
        "experience_years": 5.0,
        "linkedin_url": "https://linkedin.com/in/harsh-agarwal-fe",
        "github_url": "https://github.com/harsh-mfe",
        "website_url": "",
        "projects": [
            {"name": "Nykaa Micro-frontend Migration", "description": "Architected Webpack Module Federation setup for 8 independent teams. Cut release cycle from 2 weeks to 2 days.", "link": ""},
            {"name": "mfe-devtools", "description": "Chrome DevTools extension for debugging micro-frontend composition and shared dependencies.", "link": "https://github.com/harsh-mfe/mfe-devtools"},
        ],
    },
    {
        "name": "Tanvi Shah",
        "summary": "UI Engineer with 1.5 years specialising in React Native Web and cross-platform component libraries. Built and shipped the design system at a Series B fintech that unified web and mobile UI with 95% component reuse. Passionate about animation and motion design.",
        "skills": ["React", "React Native Web", "TypeScript", "Reanimated 3", "Framer Motion", "Radix UI", "CSS-in-JS", "Figma"],
        "experience_years": 1.5,
        "linkedin_url": "https://linkedin.com/in/tanvi-shah-ui",
        "github_url": "https://github.com/tanvi-ui",
        "website_url": "https://tanvishah.design",
        "projects": [
            {"name": "UnifyDS — Cross-platform Design System", "description": "Radix UI + React Native Web design system with shared tokens. Used across web and mobile at Slice fintech.", "link": ""},
            {"name": "framer-spring-visualiser", "description": "Interactive tool for visualising Framer Motion spring physics. 1k+ daily active users.", "link": "https://github.com/tanvi-ui/spring-viz"},
        ],
    },
    {
        "name": "Arnav Desai",
        "summary": "Frontend developer with 2.5 years and a strong bias for web performance. Passionate about rendering patterns (SSR, ISR, streaming) in Next.js. At Groww, implemented server components migration that reduced JS bundle by 45% and improved FCP on mobile by 2 seconds.",
        "skills": ["Next.js", "React Server Components", "TypeScript", "Turbopack", "Edge Runtime", "Vercel", "SWR", "CSS Modules"],
        "experience_years": 2.5,
        "linkedin_url": "https://linkedin.com/in/arnav-desai-nextjs",
        "github_url": "https://github.com/arnav-web",
        "website_url": "https://arnavdesai.dev",
        "projects": [
            {"name": "Groww Server Components Migration", "description": "Migrated 40+ Groww pages to Next.js App Router with RSC. 45% JS bundle reduction, 2s FCP improvement.", "link": ""},
            {"name": "next-edge-middleware-kit", "description": "Collection of Next.js edge middleware patterns for A/B testing, geo-routing, and auth. 300+ GitHub stars.", "link": "https://github.com/arnav-web/next-edge-kit"},
        ],
    },
    {
        "name": "Simran Bhat",
        "summary": "Frontend engineer with 4 years building real-time collaborative interfaces. Expert in WebSocket state management, CRDT-based conflict resolution, and rich text editors (Slate.js, TipTap). At Notion-competitor startup Cospace, built the real-time document engine handling 50k concurrent users.",
        "skills": ["React", "WebSocket", "Slate.js", "TipTap", "CRDT", "Zustand", "TypeScript", "WebRTC"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/simran-bhat-realtime",
        "github_url": "https://github.com/simran-realtime",
        "website_url": "",
        "projects": [
            {"name": "Cospace Real-time Document Engine", "description": "CRDT-based collaborative editor supporting 50k concurrent users. Built on Slate.js with custom WebSocket sync.", "link": ""},
            {"name": "y-websocket-server", "description": "Scalable Yjs WebSocket provider using Redis pub/sub for horizontal scaling. 500+ GitHub stars.", "link": "https://github.com/simran-realtime/y-ws-redis"},
        ],
    },
    {
        "name": "Dhruv Pandey",
        "summary": "Angular specialist with 3 years building enterprise SaaS dashboards. Expert in NgRx state management, Angular Material customisation, and RxJS reactive patterns. At ThoughtWorks, delivered a financial analytics dashboard for an NBFC handling 200TB of data.",
        "skills": ["Angular", "NgRx", "RxJS", "TypeScript", "Angular Material", "D3.js", "Jasmine", "Karma"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/dhruv-pandey-angular",
        "github_url": "https://github.com/dhruv-angular",
        "website_url": "",
        "projects": [
            {"name": "NBFC Financial Analytics Dashboard", "description": "Angular + NgRx dashboard with D3.js charts. Real-time ingestion of 200TB data, built for 500 concurrent analysts.", "link": ""},
            {"name": "ngrx-persist-plus", "description": "NgRx meta-reducer for selective state persistence with IndexedDB and encryption. 400+ npm weekly downloads.", "link": "https://github.com/dhruv-angular/ngrx-persist-plus"},
        ],
    },
    {
        "name": "Aditi Mishra",
        "summary": "Junior frontend developer (1 year) with excellent foundations in React and CSS. Graduated from BITS Pilani, completed 2 production internships before full-time. Strong at converting Figma designs pixel-perfectly to code and writing accessible, semantic HTML.",
        "skills": ["React", "JavaScript", "CSS", "HTML5", "Figma", "Git", "REST API", "Tailwind CSS"],
        "experience_years": 1.0,
        "linkedin_url": "https://linkedin.com/in/aditi-mishra-frontend",
        "github_url": "https://github.com/aditi-frontend",
        "website_url": "https://aditi.codes",
        "projects": [
            {"name": "Internship: Cars24 Listing Page", "description": "Rebuilt Cars24 vehicle listing UI in React with infinite scroll and filter state. Shipped to production in 6 weeks.", "link": ""},
            {"name": "portfolio-builder", "description": "No-code portfolio builder for developers using React and local storage. 200+ users.", "link": "https://github.com/aditi-frontend/portfolio-builder"},
        ],
    },
    {
        "name": "Kunal Tiwari",
        "summary": "Frontend engineer with 3.5 years specialising in data visualisation and dashboard UI. Expert in D3.js, Recharts, and Apache ECharts for building interactive analytics interfaces. At Dream11, built the real-time game scoring dashboard serving 10M users during IPL.",
        "skills": ["React", "D3.js", "Recharts", "ECharts", "TypeScript", "WebSocket", "Canvas API", "Tailwind CSS"],
        "experience_years": 3.5,
        "linkedin_url": "https://linkedin.com/in/kunal-tiwari-dataviz",
        "github_url": "https://github.com/kunal-dataviz",
        "website_url": "",
        "projects": [
            {"name": "Dream11 Real-time Scoring UI", "description": "D3.js + WebSocket dashboard for live IPL scores serving 10M concurrent users. Sub-100ms UI updates.", "link": ""},
            {"name": "react-chart-primitives", "description": "Headless React chart primitives with D3.js under the hood and full TypeScript types. 700+ GitHub stars.", "link": "https://github.com/kunal-dataviz/react-chart-primitives"},
        ],
    },
    {
        "name": "Isha Srivastava",
        "summary": "Frontend engineer with 2 years and a strong focus on internationalisation (i18n), RTL support, and multi-language product development. At Sharechat, built the i18n infrastructure supporting 15 Indian languages with dynamic content loading and locale-aware formatting.",
        "skills": ["React", "i18next", "TypeScript", "RTL CSS", "ICU Message Format", "Next.js", "Crowdin", "Jest"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/isha-srivastava-i18n",
        "github_url": "https://github.com/isha-i18n",
        "website_url": "",
        "projects": [
            {"name": "Sharechat i18n Infrastructure", "description": "Built i18next + Crowdin pipeline supporting 15 Indian languages with dynamic loading. Zero-downtime locale switching.", "link": ""},
            {"name": "react-i18n-devtools", "description": "React DevTools extension for detecting untranslated strings and previewing locales in real-time.", "link": "https://github.com/isha-i18n/react-i18n-devtools"},
        ],
    },

    # ── BACKEND (10) ───────────────────────────────────────────────────────────

    {
        "name": "Rahul Mehta",
        "summary": "Backend engineer with 4 years of Python/FastAPI experience building high-throughput APIs and data pipelines. Expertise in async architectures, PostgreSQL optimisation, and microservices on AWS. Ex-Zerodha, designed the trade-history export service handling 5M daily requests.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Celery", "AWS", "Docker", "Kafka"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/rahulmehta-backend",
        "github_url": "https://github.com/rahulm-be",
        "website_url": "",
        "projects": [
            {"name": "Trade History Export Service", "description": "Async export pipeline at Zerodha using Celery + S3. Handles 5M rows/day with P99 latency under 200ms.", "link": ""},
            {"name": "fastapi-ratelimiter", "description": "Redis-backed sliding-window rate limiter middleware for FastAPI, 2k+ PyPI downloads/week.", "link": "https://github.com/rahulm-be/fastapi-ratelimiter"},
        ],
    },
    {
        "name": "Rohan Kapoor",
        "summary": "Senior Java/Spring Boot backend engineer with 6 years designing distributed systems for banking and fintech. Expert in microservices, event-driven architectures, and performance tuning at scale. At HDFC Bank Tech, maintained core payment APIs processing ₹4000 crore daily.",
        "skills": ["Java", "Spring Boot", "Kafka", "PostgreSQL", "Redis", "Docker", "Kubernetes", "Oracle DB"],
        "experience_years": 6.0,
        "linkedin_url": "https://linkedin.com/in/rohan-kapoor-java",
        "github_url": "https://github.com/rohankapoor-be",
        "website_url": "",
        "projects": [
            {"name": "HDFC Core Payment API", "description": "Maintained and optimised Java Spring Boot APIs processing ₹4000 crore/day. Achieved sub-50ms P99.", "link": ""},
            {"name": "spring-idempotency-starter", "description": "Spring Boot starter for distributed idempotency using Redis. Used in 3 production systems.", "link": "https://github.com/rohankapoor-be/spring-idempotency"},
        ],
    },
    {
        "name": "Varun Saxena",
        "summary": "Go backend engineer with 3 years building ultra-low latency services. Passionate about gRPC, Protocol Buffers, and systems programming. At Ola Electric, designed the vehicle telemetry ingestion service handling 2M events/second using Go and Apache Pulsar.",
        "skills": ["Go", "gRPC", "Protocol Buffers", "Apache Pulsar", "PostgreSQL", "Redis", "Docker", "Prometheus"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/varun-saxena-golang",
        "github_url": "https://github.com/varun-go",
        "website_url": "",
        "projects": [
            {"name": "Ola Electric Telemetry Service", "description": "Go microservice ingesting 2M vehicle telemetry events/second via Apache Pulsar. P99 latency: 8ms.", "link": ""},
            {"name": "grpc-health-middleware", "description": "gRPC interceptor for health checks, circuit breaking, and adaptive concurrency limits in Go.", "link": "https://github.com/varun-go/grpc-health-mw"},
        ],
    },
    {
        "name": "Pooja Chatterjee",
        "summary": "Node.js backend engineer with 2.5 years building API platforms and real-time services. Strong in TypeScript, event-driven design, and GraphQL subscriptions. At Paytm, built the notifications platform delivering 50M push/SMS/email events daily with 99.9% delivery rate.",
        "skills": ["Node.js", "TypeScript", "GraphQL", "PostgreSQL", "RabbitMQ", "Redis", "AWS Lambda", "Jest"],
        "experience_years": 2.5,
        "linkedin_url": "https://linkedin.com/in/pooja-chatterjee-nodejs",
        "github_url": "https://github.com/pooja-node",
        "website_url": "",
        "projects": [
            {"name": "Paytm Notifications Platform", "description": "Node.js event-driven platform for 50M daily notifications (push, SMS, email). 99.9% delivery SLA.", "link": ""},
            {"name": "graphql-subscription-redis", "description": "Redis pub/sub transport for GraphQL subscriptions in Apollo Server. 600+ npm weekly downloads.", "link": "https://github.com/pooja-node/graphql-sub-redis"},
        ],
    },
    {
        "name": "Manish Rao",
        "summary": "Backend engineer with 5 years in Ruby on Rails and Elixir, specialising in marketplace and e-commerce platforms. At Meesho, built the seller payout engine processing ₹500 crore monthly, and migrated the monolith's critical financial modules to Elixir for 10x throughput.",
        "skills": ["Ruby on Rails", "Elixir", "Phoenix", "PostgreSQL", "Sidekiq", "Redis", "RSpec", "AWS"],
        "experience_years": 5.0,
        "linkedin_url": "https://linkedin.com/in/manish-rao-rails",
        "github_url": "https://github.com/manishrao-be",
        "website_url": "",
        "projects": [
            {"name": "Meesho Seller Payout Engine", "description": "Rails + Elixir payout system processing ₹500 crore/month for 1.5M sellers. Idempotent, auditable.", "link": ""},
            {"name": "elixir-money", "description": "Elixir library for precise monetary arithmetic and currency conversion with ExchangeRate API support.", "link": "https://github.com/manishrao-be/elixir-money"},
        ],
    },
    {
        "name": "Akash Dubey",
        "summary": "Backend engineer with 3 years focused on search infrastructure and Elasticsearch. At Flipkart, maintained the product search service with 500M indexed documents, improving relevance through custom BM25 tuning and query expansion. Expert in Elasticsearch DSL and cluster management.",
        "skills": ["Python", "Elasticsearch", "Apache Solr", "FastAPI", "Redis", "Kafka", "PostgreSQL", "Docker"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/akash-dubey-search",
        "github_url": "https://github.com/akash-search",
        "website_url": "",
        "projects": [
            {"name": "Flipkart Product Search Tuning", "description": "BM25 parameter tuning + query expansion using synonym graphs. Improved search conversion by 12%.", "link": ""},
            {"name": "es-query-builder-py", "description": "Type-safe Elasticsearch query builder for Python with full DSL coverage and query testing utilities.", "link": "https://github.com/akash-search/es-query-builder"},
        ],
    },
    {
        "name": "Nandini Roy",
        "summary": "Backend engineer with 2 years specialising in authentication systems, OAuth2 flows, and API security. Excellent understanding of JWT, PKCE, and RBAC models. At Fi Money, designed the unified auth service used by 3 million users, with FIDO2 passkey support.",
        "skills": ["Python", "FastAPI", "OAuth2", "FIDO2", "JWT", "PostgreSQL", "Redis", "AWS Cognito"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/nandini-roy-auth",
        "github_url": "https://github.com/nandini-auth",
        "website_url": "",
        "projects": [
            {"name": "Fi Money Unified Auth Service", "description": "FastAPI auth service with FIDO2 passkeys, OAuth2 PKCE, and MFA. Serves 3M users, 99.99% uptime.", "link": ""},
            {"name": "fastapi-fido2", "description": "FIDO2/WebAuthn integration library for FastAPI with attestation validation and credential management.", "link": "https://github.com/nandini-auth/fastapi-fido2"},
        ],
    },
    {
        "name": "Rajesh Banerjee",
        "summary": "Senior backend engineer with 7 years across e-commerce and logistics. Expert in high-volume order management systems, distributed transactions, and event sourcing. At Amazon India, designed the last-mile delivery state machine handling 1M daily shipments with guaranteed exactly-once semantics.",
        "skills": ["Java", "Spring Boot", "Event Sourcing", "CQRS", "DynamoDB", "SQS", "SNS", "Kubernetes"],
        "experience_years": 7.0,
        "linkedin_url": "https://linkedin.com/in/rajesh-banerjee-backend",
        "github_url": "https://github.com/rajesh-be",
        "website_url": "",
        "projects": [
            {"name": "Amazon India Delivery State Machine", "description": "Event-sourced order state machine with exactly-once delivery guarantees. Handles 1M shipments/day.", "link": ""},
            {"name": "saga-pattern-spring", "description": "Saga pattern implementation for distributed transactions in Spring Boot using Kafka and compensating transactions.", "link": "https://github.com/rajesh-be/saga-spring"},
        ],
    },
    {
        "name": "Abhijit Das",
        "summary": "Backend engineer with 1.5 years experience in Python and Go, passionate about building reliable microservices. Strong computer science fundamentals from IIT Kharagpur. Has shipped 3 production APIs at a Bangalore fintech startup, with emphasis on testing and observability.",
        "skills": ["Python", "Go", "FastAPI", "PostgreSQL", "Docker", "Prometheus", "OpenTelemetry", "pytest"],
        "experience_years": 1.5,
        "linkedin_url": "https://linkedin.com/in/abhijit-das-backend",
        "github_url": "https://github.com/abhijit-iitk",
        "website_url": "",
        "projects": [
            {"name": "Lending Startup KYC API", "description": "FastAPI KYC microservice integrating DigiLocker, PAN, and Aadhaar verification. Handles 10k verifications/day.", "link": ""},
            {"name": "opentelemetry-fastapi-auto", "description": "Zero-config OpenTelemetry auto-instrumentation for FastAPI with Jaeger and Prometheus exporters.", "link": "https://github.com/abhijit-iitk/otel-fastapi"},
        ],
    },
    {
        "name": "Sonal Verma",
        "summary": "Backend engineer with 4 years in the media and streaming industry. Expert in video processing pipelines, HLS/DASH streaming, and content delivery optimisation. At JioCinema, built the adaptive bitrate encoding pipeline that reduced CDN costs by 30% while maintaining streaming quality.",
        "skills": ["Python", "FFmpeg", "AWS MediaConvert", "S3", "CloudFront", "FastAPI", "Redis", "Celery"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/sonal-verma-media",
        "github_url": "https://github.com/sonal-media",
        "website_url": "",
        "projects": [
            {"name": "JioCinema ABR Encoding Pipeline", "description": "Python + AWS MediaConvert pipeline for 4K HLS encoding. Reduced CDN costs by 30% via per-title encoding.", "link": ""},
            {"name": "video-quality-metrics", "description": "CLI tool for computing VMAF, SSIM, and PSNR scores against reference videos using FFmpeg and Python.", "link": "https://github.com/sonal-media/video-quality-metrics"},
        ],
    },

    # ── FULL-STACK (8) ─────────────────────────────────────────────────────────

    {
        "name": "Arjun Nair",
        "summary": "Full-stack engineer (MERN + Python) with 2 years building SaaS products from scratch. Comfortable owning features end-to-end, from React frontends to Node.js APIs and MongoDB schemas. Freelanced for 3 startups before joining Cred's growth team.",
        "skills": ["React", "Node.js", "MongoDB", "Express", "Python", "Docker", "TypeScript", "AWS S3"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/arjun-nair-fullstack",
        "github_url": "https://github.com/arjun-nair-dev",
        "website_url": "",
        "projects": [
            {"name": "Cred Referral Engine", "description": "Built A/B-tested referral flows in React + Node.js that drove 18% signup lift in Q3 2024.", "link": ""},
            {"name": "OpenBilling (OSS)", "description": "Self-hosted billing SaaS for Indian startups supporting UPI/Razorpay webhooks. MERN stack.", "link": "https://github.com/arjun-nair-dev/openbilling"},
        ],
    },
    {
        "name": "Meera Iyer",
        "summary": "Full-stack product engineer with 3.5 years in Python/Django backend and React frontend. Comfortable across the stack — owns features from database schema to deployed UI. At Urban Company, built the service partner matching engine that improved booking conversion by 22%.",
        "skills": ["Python", "Django", "React", "PostgreSQL", "Celery", "Redis", "TypeScript", "REST API"],
        "experience_years": 3.5,
        "linkedin_url": "https://linkedin.com/in/meera-iyer-engineer",
        "github_url": "https://github.com/meera-fullstack",
        "website_url": "",
        "projects": [
            {"name": "Urban Company Partner Matching", "description": "Django ML scoring engine matching service requests with partner profiles. +22% booking conversion.", "link": ""},
            {"name": "django-cacheops-extension", "description": "Declarative cache invalidation for Django with Redis. 150+ GitHub stars.", "link": "https://github.com/meera-fullstack/django-cacheops-ext"},
        ],
    },
    {
        "name": "Karan Malhotra",
        "summary": "Full-stack developer (1.5 years) with a strong foundation in Next.js, Node.js, and MongoDB. Passionate about developer tooling and open source. Built a SaaS boilerplate used by 500+ developers, and currently contributing to the LangChain.js project.",
        "skills": ["Next.js", "Node.js", "MongoDB", "TypeScript", "Prisma", "tRPC", "Tailwind CSS", "Vercel"],
        "experience_years": 1.5,
        "linkedin_url": "https://linkedin.com/in/karan-malhotra-dev",
        "github_url": "https://github.com/karan-builds",
        "website_url": "https://karanmalhotra.dev",
        "projects": [
            {"name": "NextStack Boilerplate", "description": "Next.js 14 + tRPC + Prisma SaaS starter with auth, billing, and team management. 500+ GitHub forks.", "link": "https://github.com/karan-builds/nextstack"},
            {"name": "LangChain.js Contributions", "description": "Added streaming support to the Groq integration and fixed memory serialisation bugs in LangChain.js.", "link": "https://github.com/langchain-ai/langchainjs"},
        ],
    },
    {
        "name": "Neha Gupta",
        "summary": "Full-stack engineer with 4 years in the health-tech space. Backend in Python/Flask, frontend in React with strong TypeScript skills. At Practo, built the teleconsultation platform used by 2M patients monthly, integrating WebRTC for video calls and a FHIR-compliant health records API.",
        "skills": ["Python", "Flask", "React", "WebRTC", "FHIR", "PostgreSQL", "TypeScript", "AWS"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/neha-gupta-healthtech",
        "github_url": "https://github.com/neha-healthtech",
        "website_url": "",
        "projects": [
            {"name": "Practo Teleconsultation Platform", "description": "WebRTC + FHIR full-stack platform for 2M monthly doctor-patient video consultations.", "link": ""},
            {"name": "fhir-python-client", "description": "Typed Python client for FHIR R4 resources with validation and search query builder. 300+ PyPI downloads/day.", "link": "https://github.com/neha-healthtech/fhir-py"},
        ],
    },
    {
        "name": "Tarun Mishra",
        "summary": "Full-stack developer with 3 years focused on SaaS analytics products. Specialises in React dashboards backed by FastAPI with real-time updates via WebSocket and Server-Sent Events. At Zoho Analytics, built embedded analytics components used by 5000+ enterprise customers.",
        "skills": ["React", "FastAPI", "Python", "PostgreSQL", "WebSocket", "SSE", "Redis", "Docker"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/tarun-mishra-analytics",
        "github_url": "https://github.com/tarun-saas",
        "website_url": "",
        "projects": [
            {"name": "Zoho Analytics Embedded Widgets", "description": "React embedded analytics components with SSE-based live data. Used by 5000+ enterprise customers.", "link": ""},
            {"name": "fastapi-sse-manager", "description": "Server-Sent Events connection manager for FastAPI with auto-reconnect and per-user channel multiplexing.", "link": "https://github.com/tarun-saas/fastapi-sse"},
        ],
    },
    {
        "name": "Kritika Mukherjee",
        "summary": "Full-stack engineer (2.5 years) with special interest in developer tools and CLI products. Built a Raycast extension used by 3k+ developers daily, and maintains an open-source Next.js + Postgres starter template. Skilled in Rust for CLI tooling alongside TypeScript for web.",
        "skills": ["TypeScript", "Next.js", "Rust", "PostgreSQL", "Prisma", "Node.js", "React", "CLI Tools"],
        "experience_years": 2.5,
        "linkedin_url": "https://linkedin.com/in/kritika-mukherjee-devtools",
        "github_url": "https://github.com/kritika-dev",
        "website_url": "https://kritika.dev",
        "projects": [
            {"name": "Raycast GitHub Extension", "description": "Raycast extension for GitHub PR review, issue triage, and repo search. 3k+ active users.", "link": "https://github.com/kritika-dev/raycast-github"},
            {"name": "next-postgres-starter", "description": "Next.js 14 + Prisma + PostgreSQL starter with row-level security and server actions. 800+ GitHub stars.", "link": "https://github.com/kritika-dev/next-pg-starter"},
        ],
    },
    {
        "name": "Kabir Pandey",
        "summary": "Senior full-stack engineer with 6 years building marketplace platforms. Deep expertise in multi-tenant SaaS architecture, complex pricing engines, and payment integrations. At OYO, designed the property revenue management system that auto-adjusts 1M+ room prices daily based on demand signals.",
        "skills": ["React", "Node.js", "Python", "PostgreSQL", "Redis", "Kafka", "TypeScript", "AWS"],
        "experience_years": 6.0,
        "linkedin_url": "https://linkedin.com/in/kabir-pandey-marketplace",
        "github_url": "https://github.com/kabir-fullstack",
        "website_url": "",
        "projects": [
            {"name": "OYO Revenue Management System", "description": "Python + Node.js dynamic pricing engine adjusting 1M+ room prices daily using demand signals and ML models.", "link": ""},
            {"name": "multi-tenant-pg", "description": "PostgreSQL multi-tenancy toolkit with row-level security, schema isolation, and tenant-aware connection pooling.", "link": "https://github.com/kabir-fullstack/multi-tenant-pg"},
        ],
    },
    {
        "name": "Riya Chatterjee",
        "summary": "Full-stack engineer with 2 years and a strong background in fintech product development. Experienced with React, FastAPI, and real-time financial data. At Jupiter, built the transaction categorisation UI and the backend ML tagging service that classifies 5M transactions daily.",
        "skills": ["React", "FastAPI", "Python", "PostgreSQL", "scikit-learn", "TypeScript", "Redis", "Docker"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/riya-chatterjee-fintech",
        "github_url": "https://github.com/riya-fullstack",
        "website_url": "",
        "projects": [
            {"name": "Jupiter Transaction Categorisation", "description": "React UI + FastAPI + ML pipeline classifying 5M daily transactions into 40+ categories. 94% accuracy.", "link": ""},
            {"name": "plaid-india-mock", "description": "Open-source mock Plaid-equivalent API for Indian banks using UPI statement parsing. Used in hackathons.", "link": "https://github.com/riya-fullstack/plaid-india-mock"},
        ],
    },

    # ── ML / AI (6) ────────────────────────────────────────────────────────────

    {
        "name": "Ananya Krishnan",
        "summary": "ML Engineer with 2.5 years turning research models into production ML systems. Focused on NLP, LLM fine-tuning, and RAG pipelines. Built a document Q&A system at PhonePe that reduced support tickets by 35% using LangChain and Qdrant.",
        "skills": ["Python", "PyTorch", "LangChain", "Hugging Face", "Qdrant", "FastAPI", "LLM Fine-tuning", "MLflow"],
        "experience_years": 2.5,
        "linkedin_url": "https://linkedin.com/in/ananya-krishnan-ml",
        "github_url": "https://github.com/ananya-ml",
        "website_url": "https://ananyakrishnan.ai",
        "projects": [
            {"name": "PhonePe Support Doc Q&A", "description": "RAG pipeline over 50k support articles using LangChain + Qdrant. Cut Level-1 support tickets by 35%.", "link": ""},
            {"name": "IndicBERT Intent Classifier", "description": "Fine-tuned IndicBERT on 100k Hindi-English intent examples for voice assistant routing. 91% accuracy.", "link": "https://github.com/ananya-ml/indicbert-intent"},
        ],
    },
    {
        "name": "Zara Ahmed",
        "summary": "AI/LLM Engineer with 1.5 years focused on applied generative AI — prompt engineering, LLM evaluation, and agentic workflows. Built LangGraph multi-agent pipelines for enterprise document automation at a Bangalore AI startup. Strong Python and LangChain background.",
        "skills": ["Python", "LangChain", "LangGraph", "OpenAI API", "Groq", "Qdrant", "Prompt Engineering", "FastAPI"],
        "experience_years": 1.5,
        "linkedin_url": "https://linkedin.com/in/zara-ahmed-ai",
        "github_url": "https://github.com/zara-llm",
        "website_url": "https://zaraahmed.io",
        "projects": [
            {"name": "Contract Analysis Agent", "description": "LangGraph multi-agent pipeline extracting and flagging risks in legal contracts. 90% accuracy vs manual review.", "link": ""},
            {"name": "llm-eval-toolkit", "description": "LLM evaluation framework with RAGAS integration. Supports custom metrics and CI scoring.", "link": "https://github.com/zara-llm/llm-eval-toolkit"},
        ],
    },
    {
        "name": "Disha Gupta",
        "summary": "Data Scientist with 4 years building predictive models across e-commerce and healthcare. Skilled in feature engineering, gradient boosting, and model monitoring in production. At Flipkart, built a demand forecasting model that reduced inventory waste by $1.2M annually.",
        "skills": ["Python", "scikit-learn", "XGBoost", "LightGBM", "SQL", "Pandas", "MLflow", "Plotly"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/disha-gupta-ds",
        "github_url": "https://github.com/disha-datascience",
        "website_url": "https://dishagupta.notion.site",
        "projects": [
            {"name": "Flipkart Demand Forecasting", "description": "LightGBM time-series model for 2M+ SKUs. Reduced inventory overstock by 18%, saving $1.2M/year.", "link": ""},
            {"name": "feature-store-lite", "description": "Lightweight feature store using pandas + Redis to eliminate train/serve feature skew.", "link": "https://github.com/disha-datascience/feature-store-lite"},
        ],
    },
    {
        "name": "Pranav Iyer",
        "summary": "Computer Vision engineer with 3 years applying deep learning to manufacturing and quality control. Expert in PyTorch, YOLO variants, and deploying models on edge hardware. At Tata Steel, built an automated visual defect detection system that replaced 30 manual inspection stations.",
        "skills": ["Python", "PyTorch", "YOLOv8", "OpenCV", "TensorRT", "ONNX", "Edge AI", "FastAPI"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/pranav-iyer-cv",
        "github_url": "https://github.com/pranav-cv",
        "website_url": "",
        "projects": [
            {"name": "Tata Steel Visual Defect Detection", "description": "YOLOv8 + TensorRT system detecting 12 steel defect types at 99.1% precision. Replaced 30 inspection stations.", "link": ""},
            {"name": "torch-edge-deploy", "description": "Toolkit for optimising PyTorch models for edge devices using ONNX, TensorRT, and quantisation.", "link": "https://github.com/pranav-cv/torch-edge-deploy"},
        ],
    },
    {
        "name": "Shreya Bose",
        "summary": "MLOps engineer with 2 years bridging the gap between ML research and production deployment. Expert in Kubeflow, MLflow experiment tracking, and building reproducible training pipelines. At MakeMyTrip, built the model registry and A/B testing infrastructure for 12 production ML models.",
        "skills": ["Python", "Kubeflow", "MLflow", "Docker", "Kubernetes", "Airflow", "Terraform", "Prometheus"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/shreya-bose-mlops",
        "github_url": "https://github.com/shreya-mlops",
        "website_url": "",
        "projects": [
            {"name": "MakeMyTrip ML Platform", "description": "Kubeflow + MLflow platform managing lifecycle for 12 production models. Automated retraining, shadow scoring, rollback.", "link": ""},
            {"name": "mlflow-kubernetes-deploy", "description": "Helm chart + GitHub Actions workflow for zero-downtime MLflow model deployments on Kubernetes.", "link": "https://github.com/shreya-mlops/mlflow-k8s"},
        ],
    },
    {
        "name": "Ayaan Kapoor",
        "summary": "Recommender systems engineer with 5 years building personalisation at scale. Expert in collaborative filtering, two-tower neural models, and real-time feature serving. At Hotstar, redesigned the content recommendation engine that increased avg session duration by 28%.",
        "skills": ["Python", "PyTorch", "Spark", "Redis", "Kafka", "Feast", "Faiss", "AWS SageMaker"],
        "experience_years": 5.0,
        "linkedin_url": "https://linkedin.com/in/ayaan-kapoor-recsys",
        "github_url": "https://github.com/ayaan-recsys",
        "website_url": "",
        "projects": [
            {"name": "Hotstar Content Recommendations", "description": "Two-tower neural model + Faiss ANN index. Increased avg session duration by 28% for 300M users.", "link": ""},
            {"name": "recsys-eval-harness", "description": "Evaluation harness for recommendation systems with offline metrics (NDCG, MRR, Hit@K) and simulation tools.", "link": "https://github.com/ayaan-recsys/recsys-eval"},
        ],
    },

    # ── DEVOPS / CLOUD (5) ─────────────────────────────────────────────────────

    {
        "name": "Vikram Singh",
        "summary": "Senior DevOps and Cloud Infrastructure engineer with 6 years on AWS/GCP. Certified AWS Solutions Architect. Designed zero-downtime CI/CD pipelines and Kubernetes clusters serving 50M requests/day. Implemented FinOps strategies saving $200k/year at Swiggy.",
        "skills": ["Kubernetes", "Terraform", "AWS", "GCP", "Docker", "GitHub Actions", "ArgoCD", "Prometheus"],
        "experience_years": 6.0,
        "linkedin_url": "https://linkedin.com/in/vikram-singh-devops",
        "github_url": "https://github.com/vikram-infra",
        "website_url": "",
        "projects": [
            {"name": "Swiggy K8s Platform Migration", "description": "Migrated 200+ microservices from EC2 to EKS. Achieved 99.99% uptime SLA, saved $200k/year.", "link": ""},
            {"name": "terraform-aws-eks-blueprint", "description": "Production-ready Terraform module for EKS with auto-scaling, IRSA, and Karpenter. 1.2k GitHub stars.", "link": "https://github.com/vikram-infra/tf-eks-bp"},
        ],
    },
    {
        "name": "Siddharth Joshi",
        "summary": "Cloud Architect with 7 years designing multi-cloud enterprise platforms. AWS Certified Solutions Architect Professional. Designed the cloud migration strategy for a 500-person fintech from on-prem to AWS, completing in 8 months with zero service disruption.",
        "skills": ["AWS", "Azure", "Terraform", "Kubernetes", "Python", "System Design", "Security", "Cost Optimisation"],
        "experience_years": 7.0,
        "linkedin_url": "https://linkedin.com/in/siddharthjoshi-architect",
        "github_url": "https://github.com/siddharth-cloud",
        "website_url": "https://siddharthjoshi.com",
        "projects": [
            {"name": "Fintech Cloud Migration", "description": "Led 8-month on-prem → AWS migration for 500-person company. Zero downtime, 40% infra cost reduction.", "link": ""},
            {"name": "multi-cloud-landing-zone", "description": "Terraform module for enterprise AWS/Azure landing zones with networking, IAM, and compliance guardrails.", "link": "https://github.com/siddharth-cloud/mc-lz"},
        ],
    },
    {
        "name": "Varsha Pillai",
        "summary": "Platform engineer with 3 years building internal developer platforms (IDP). Passionate about developer experience, golden paths, and platform abstractions. At Atlassian India, built a self-service platform used by 800+ engineers to provision infrastructure and deploy services in under 5 minutes.",
        "skills": ["Backstage", "Kubernetes", "Terraform", "TypeScript", "GitHub Actions", "Vault", "ArgoCD", "Python"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/varsha-pillai-platform",
        "github_url": "https://github.com/varsha-platform",
        "website_url": "",
        "projects": [
            {"name": "Atlassian Internal Developer Platform", "description": "Backstage-based IDP for 800+ engineers. Self-service provisioning, service catalog, and one-click deployments.", "link": ""},
            {"name": "backstage-terraform-plugin", "description": "Backstage plugin that surfaces Terraform workspace state and enables plan/apply from the dev portal.", "link": "https://github.com/varsha-platform/backstage-tf-plugin"},
        ],
    },
    {
        "name": "Nikhil Sharma",
        "summary": "Site Reliability Engineer with 4 years maintaining high-availability systems. Expert in observability stacks (OpenTelemetry, Grafana, Loki), incident management, and chaos engineering. At Zomato, reduced MTTR from 45 minutes to 8 minutes through automated runbooks and alert correlation.",
        "skills": ["Kubernetes", "OpenTelemetry", "Grafana", "Prometheus", "Loki", "Python", "PagerDuty", "Chaos Mesh"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/nikhil-sharma-sre",
        "github_url": "https://github.com/nikhil-sre",
        "website_url": "",
        "projects": [
            {"name": "Zomato SRE Observability Stack", "description": "Built unified OpenTelemetry + Grafana + Loki observability. Reduced MTTR from 45min to 8min.", "link": ""},
            {"name": "k8s-chaos-operator", "description": "Kubernetes operator for scheduled chaos experiments with automatic rollback and Slack alerting.", "link": "https://github.com/nikhil-sre/k8s-chaos-op"},
        ],
    },
    {
        "name": "Aarav Bhat",
        "summary": "Cloud engineer with 2 years specialising in serverless architectures and cost optimisation on AWS. Helped 3 startups cut cloud bills by 40-60% through reserved instance strategy, Lambda rightsizing, and S3 lifecycle policies. Strong IaC skills with Terraform and AWS CDK.",
        "skills": ["AWS Lambda", "AWS CDK", "Terraform", "Python", "DynamoDB", "S3", "CloudFormation", "Cost Explorer"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/aarav-bhat-cloud",
        "github_url": "https://github.com/aarav-aws",
        "website_url": "",
        "projects": [
            {"name": "Startup Cloud Cost Audit Tool", "description": "Python + AWS CDK tool that analyses Cost Explorer data and generates actionable saving recommendations.", "link": "https://github.com/aarav-aws/aws-cost-audit"},
            {"name": "serverless-patterns-india", "description": "Collection of production-ready AWS serverless patterns optimised for Indian compliance (DPDP, RBI) requirements.", "link": "https://github.com/aarav-aws/serverless-patterns-india"},
        ],
    },

    # ── MOBILE (4) ─────────────────────────────────────────────────────────────

    {
        "name": "Sneha Patel",
        "summary": "React Native mobile developer with 3.5 years building cross-platform apps on iOS and Android. Deep expertise in Expo, Reanimated 3, and offline-first architectures. Led mobile at a Sequoia-backed fintech, shipped an app used by 1M+ monthly users.",
        "skills": ["React Native", "Expo", "TypeScript", "Reanimated", "Redux Toolkit", "Firebase", "Xcode", "Fastlane"],
        "experience_years": 3.5,
        "linkedin_url": "https://linkedin.com/in/sneha-patel-mobile",
        "github_url": "https://github.com/snehapatel-rn",
        "website_url": "https://snehapatel.in",
        "projects": [
            {"name": "FinWallet Mobile App", "description": "Led React Native rewrite of legacy iOS/Android fintech app. 4.8* App Store rating, 1M MAU.", "link": ""},
            {"name": "rn-haptics-kit", "description": "Haptic feedback library for React Native with gesture-sync support. 600+ GitHub stars.", "link": "https://github.com/snehapatel-rn/rn-haptics-kit"},
        ],
    },
    {
        "name": "Aditya Kumar",
        "summary": "Flutter mobile developer with 2 years building beautiful, performant apps for Android and iOS. Strong Dart skills, experience with BLoC state management and Firebase integration. Published 2 apps on Play Store with 50k+ combined installs.",
        "skills": ["Flutter", "Dart", "Firebase", "BLoC", "REST API", "Hive", "GetX", "Codemagic CI/CD"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/aditya-kumar-flutter",
        "github_url": "https://github.com/aditya-flutter",
        "website_url": "",
        "projects": [
            {"name": "HabitFlow (Play Store)", "description": "Flutter habit tracking app with offline-first Hive storage and Firebase sync. 30k installs, 4.6* rating.", "link": "https://play.google.com/store"},
            {"name": "flutter-custom-charts", "description": "Highly customisable chart widgets for Flutter using CustomPainter. 400+ GitHub stars.", "link": "https://github.com/aditya-flutter/flutter-custom-charts"},
        ],
    },
    {
        "name": "Ishita Kapoor",
        "summary": "iOS engineer with 3 years building Swift/SwiftUI apps. Expert in Core Data, CloudKit sync, and App Clips. At Swiggy, led the iOS app's 'order tracking' redesign using SwiftUI + MapKit, increasing in-app delivery tracking engagement by 65%.",
        "skills": ["Swift", "SwiftUI", "Core Data", "Combine", "CloudKit", "MapKit", "Xcode", "TestFlight"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/ishita-kapoor-ios",
        "github_url": "https://github.com/ishita-ios",
        "website_url": "",
        "projects": [
            {"name": "Swiggy iOS Order Tracking", "description": "SwiftUI + MapKit order tracking UI. 65% increase in engagement during delivery. Smooth 60fps animations.", "link": ""},
            {"name": "swift-networking-layer", "description": "Protocol-oriented Swift networking layer with request deduplication, retry logic, and offline queue.", "link": "https://github.com/ishita-ios/swift-net"},
        ],
    },
    {
        "name": "Shubham Saxena",
        "summary": "Android engineer with 4 years in Kotlin and Jetpack Compose. Strong in architecture patterns (MVI, MVVM), performance profiling, and reducing app size. At Zepto, reduced cold start time by 70% and app size by 35% through baseline profiles and resource optimisation.",
        "skills": ["Kotlin", "Jetpack Compose", "Android", "Coroutines", "Room", "Retrofit", "Hilt", "Baseline Profiles"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/shubham-saxena-android",
        "github_url": "https://github.com/shubham-android",
        "website_url": "",
        "projects": [
            {"name": "Zepto Android Performance", "description": "Baseline profiles + R8 rules + WebP migration reduced cold start by 70% and APK size by 35%.", "link": ""},
            {"name": "compose-shimmer", "description": "Jetpack Compose shimmer loading effect library with gradient customisation. 800+ GitHub stars.", "link": "https://github.com/shubham-android/compose-shimmer"},
        ],
    },

    # ── DATA ENGINEERING & SCIENCE (4) ─────────────────────────────────────────

    {
        "name": "Ishaan Verma",
        "summary": "Data Engineer with 2 years building batch and streaming data pipelines on AWS and GCP. Experienced with dbt, Airflow, and BigQuery. At Meesho, built the seller analytics data warehouse ingesting 10TB/day, enabling real-time inventory reporting for 1.5M sellers.",
        "skills": ["Python", "Apache Spark", "Airflow", "dbt", "BigQuery", "Snowflake", "Kafka", "SQL"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/ishaan-verma-data",
        "github_url": "https://github.com/ishaan-de",
        "website_url": "",
        "projects": [
            {"name": "Meesho Seller Analytics DWH", "description": "dbt + BigQuery warehouse ingesting 10TB/day. Powers real-time seller dashboard for 1.5M sellers.", "link": ""},
            {"name": "airflow-cosmos-template", "description": "Airflow + dbt-core integration template using Cosmos. 300+ GitHub forks.", "link": "https://github.com/ishaan-de/airflow-cosmos-template"},
        ],
    },
    {
        "name": "Pooja Rao",
        "summary": "Senior data engineer with 5 years architecting lakehouse platforms. Expert in Apache Iceberg, Delta Lake, and Apache Flink for real-time stream processing. At Reliance Jio, designed a data lakehouse ingesting 500TB/day of network telemetry, reducing reporting latency from 24 hours to 5 minutes.",
        "skills": ["Apache Flink", "Apache Iceberg", "PySpark", "Scala", "dbt", "Databricks", "Kafka", "Trino"],
        "experience_years": 5.0,
        "linkedin_url": "https://linkedin.com/in/pooja-rao-dataeng",
        "github_url": "https://github.com/pooja-lakehouse",
        "website_url": "",
        "projects": [
            {"name": "Jio Network Telemetry Lakehouse", "description": "Apache Iceberg + Flink lakehouse ingesting 500TB/day. Reduced reporting latency from 24h to 5min.", "link": ""},
            {"name": "iceberg-partition-advisor", "description": "Tool that analyses Iceberg table metrics and recommends optimal partition evolution strategies.", "link": "https://github.com/pooja-lakehouse/iceberg-partition-advisor"},
        ],
    },
    {
        "name": "Suresh Nambiar",
        "summary": "Analytics engineer with 3 years building business intelligence infrastructure with dbt and Redshift. Strong at translating complex business logic into clean SQL models and building self-serve dashboards. At Byju's, built the student engagement data mart powering 150+ executive dashboards.",
        "skills": ["dbt", "SQL", "Redshift", "Looker", "Python", "Airflow", "BigQuery", "Tableau"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/suresh-nambiar-analytics",
        "github_url": "https://github.com/suresh-analytics",
        "website_url": "",
        "projects": [
            {"name": "Byju's Student Engagement Data Mart", "description": "dbt + Redshift mart with 200+ models powering 150 Looker dashboards for 500k daily active students.", "link": ""},
            {"name": "dbt-contract-tests", "description": "dbt package adding schema contract testing with breaking change detection for CI pipelines.", "link": "https://github.com/suresh-analytics/dbt-contract-tests"},
        ],
    },
    {
        "name": "Varsha Nair",
        "summary": "Data scientist with 3 years applying statistical modelling to marketing and growth problems. Expert in causal inference, A/B testing design, and marketing mix modelling. At Myntra, ran 200+ experiments per quarter and built an MMM that reallocated ₹50 crore in ad spend for 18% better ROAS.",
        "skills": ["Python", "R", "Pymc3", "statsmodels", "SQL", "A/B Testing", "Causal Inference", "Pandas"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/varsha-nair-datascience",
        "github_url": "https://github.com/varsha-causal",
        "website_url": "",
        "projects": [
            {"name": "Myntra Marketing Mix Model", "description": "Bayesian MMM using Pymc3 that reallocated ₹50 crore ad spend, improving blended ROAS by 18%.", "link": ""},
            {"name": "ab-test-calculator-india", "description": "A/B test calculator accounting for Indian traffic seasonality (festivals, sales) with MDE and power analysis.", "link": "https://github.com/varsha-causal/ab-calc-india"},
        ],
    },

    # ── QA / TESTING (3) ───────────────────────────────────────────────────────

    {
        "name": "Amitesh Roy",
        "summary": "Senior QA / SDET with 5 years building test automation frameworks. Expert in Playwright, Cypress, and API testing with Python. At Freshworks, built an end-to-end test suite covering 2000+ user flows that runs in 12 minutes in CI, catching 95% of regressions before release.",
        "skills": ["Playwright", "Cypress", "Python", "pytest", "Postman", "k6", "Docker", "GitHub Actions"],
        "experience_years": 5.0,
        "linkedin_url": "https://linkedin.com/in/amitesh-roy-qa",
        "github_url": "https://github.com/amitesh-qa",
        "website_url": "",
        "projects": [
            {"name": "Freshworks E2E Test Suite", "description": "Playwright + pytest framework with 2000+ tests running in 12min CI. 95% regression detection rate.", "link": ""},
            {"name": "playwright-page-factory", "description": "Page Object Model factory for Playwright with auto-wait strategies and accessibility assertion helpers.", "link": "https://github.com/amitesh-qa/playwright-pof"},
        ],
    },
    {
        "name": "Preethi Selvam",
        "summary": "Performance testing engineer with 3 years identifying and resolving scalability bottlenecks. Expert in k6, JMeter, and Gatling for load testing, with strong profiling skills in Java and Python. At Ola, performance-tested the ride booking API to certify 500k concurrent user capacity before IPL surge.",
        "skills": ["k6", "JMeter", "Gatling", "Python", "Java", "Grafana", "Prometheus", "AWS"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/preethi-selvam-perf",
        "github_url": "https://github.com/preethi-perf",
        "website_url": "",
        "projects": [
            {"name": "Ola Surge Capacity Testing", "description": "k6 + Grafana load testing certifying 500k concurrent users for IPL event surge. Found and fixed 3 DB bottlenecks.", "link": ""},
            {"name": "k6-influx-reporter", "description": "k6 extension for publishing test metrics to InfluxDB with custom SLO threshold alerting.", "link": "https://github.com/preethi-perf/k6-influx"},
        ],
    },
    {
        "name": "Rohan Das",
        "summary": "Mobile QA engineer with 2 years specialising in iOS and Android test automation using Appium and XCTest. Expert in building device farm workflows and flakiness reduction strategies. At Lenskart, automated the critical purchase funnel across 50 device configurations, reducing manual QA effort by 70%.",
        "skills": ["Appium", "XCTest", "Espresso", "Python", "BrowserStack", "TestNG", "Fastlane", "GitHub Actions"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/rohan-das-mobileqa",
        "github_url": "https://github.com/rohan-mobileqa",
        "website_url": "",
        "projects": [
            {"name": "Lenskart Purchase Funnel Automation", "description": "Appium + BrowserStack test suite across 50 device configs. 70% reduction in manual QA cycle time.", "link": ""},
            {"name": "appium-retry-handler", "description": "Appium test retry handler with flakiness scoring, session reuse, and Slack failure digests.", "link": "https://github.com/rohan-mobileqa/appium-retry"},
        ],
    },

    # ── SECURITY (3) ───────────────────────────────────────────────────────────

    {
        "name": "Akshay Pillai",
        "summary": "Application security engineer with 4 years conducting penetration testing and threat modelling. CEH and OSCP certified. At Razorpay, led the security review of the payment API surface area (PCI-DSS scope), reducing high-severity findings by 85% over two years.",
        "skills": ["Penetration Testing", "OWASP", "Burp Suite", "Python", "PCI-DSS", "SAST/DAST", "AWS Security", "CTF"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/akshay-pillai-security",
        "github_url": "https://github.com/akshay-appsec",
        "website_url": "",
        "projects": [
            {"name": "Razorpay PCI-DSS Security Audit", "description": "Led pentest and threat modelling of payment API surface. Reduced high-severity findings by 85%.", "link": ""},
            {"name": "api-security-scanner", "description": "Python CLI tool for automated REST API security scanning (BOLA, injection, auth bypass). 400+ GitHub stars.", "link": "https://github.com/akshay-appsec/api-scanner"},
        ],
    },
    {
        "name": "Deepika Singh",
        "summary": "Cloud security and IAM engineer with 3 years securing AWS and GCP environments for regulated industries. Expert in policy-as-code, CSPM, and zero-trust architecture. At ICICI Bank Tech, implemented an AWS Organization security baseline reducing attack surface by 60%.",
        "skills": ["AWS IAM", "OPA", "Terraform", "AWS Security Hub", "GuardDuty", "Python", "Falco", "CSPM"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/deepika-singh-cloudsec",
        "github_url": "https://github.com/deepika-cloudsec",
        "website_url": "",
        "projects": [
            {"name": "ICICI AWS Security Baseline", "description": "OPA + Terraform Sentinel policies enforcing security guardrails across 50+ AWS accounts. Reduced findings by 60%.", "link": ""},
            {"name": "iam-analyzer-cli", "description": "CLI tool that analyses IAM policies for privilege escalation paths using IAM Access Analyzer APIs.", "link": "https://github.com/deepika-cloudsec/iam-analyzer"},
        ],
    },
    {
        "name": "Farhan Sheikh",
        "summary": "Security engineer with 2 years focused on DevSecOps and shifting security left. Expert in integrating SAST (Semgrep), SCA (Snyk), and secrets scanning into CI/CD pipelines. At Groww, built the security scanning pipeline that covers 100% of code changes with zero developer friction.",
        "skills": ["Semgrep", "Snyk", "GitHub Actions", "Python", "Trivy", "gitleaks", "Docker Security", "SBOM"],
        "experience_years": 2.0,
        "linkedin_url": "https://linkedin.com/in/farhan-sheikh-devsecops",
        "github_url": "https://github.com/farhan-security",
        "website_url": "",
        "projects": [
            {"name": "Groww DevSecOps Pipeline", "description": "Semgrep + Snyk + gitleaks pipeline covering 100% of commits. 0% false positive tuning over 6 months.", "link": ""},
            {"name": "semgrep-rules-india-compliance", "description": "Semgrep custom rules for DPDP Act, RBI IT Framework, and SEBI CSCRF compliance checks.", "link": "https://github.com/farhan-security/semgrep-india"},
        ],
    },

    # ── PRODUCT / GENERALIST (4) ───────────────────────────────────────────────

    {
        "name": "Priya Krishnamurthy",
        "summary": "Product engineer with 4 years combining strong engineering skills with product intuition. Comfortable moving from user research to API design to React implementation. At Unacademy, owned the live classes feature end-to-end, growing usage by 3x and reducing dropout rates by 25%.",
        "skills": ["React", "Python", "FastAPI", "PostgreSQL", "Product Analytics", "A/B Testing", "TypeScript", "Mixpanel"],
        "experience_years": 4.0,
        "linkedin_url": "https://linkedin.com/in/priya-krishnamurthy-pe",
        "github_url": "https://github.com/priyak-product",
        "website_url": "",
        "projects": [
            {"name": "Unacademy Live Classes Redesign", "description": "Owned full feature lifecycle from interviews to production. 3x usage growth, 25% dropout reduction.", "link": ""},
            {"name": "analytics-event-schema", "description": "JSON Schema-based analytics event governance tool. Prevents schema drift in high-volume product analytics.", "link": "https://github.com/priyak-product/analytics-schema"},
        ],
    },
    {
        "name": "Nitin Agarwal",
        "summary": "Engineer with 3 years and a background spanning backend APIs, data engineering, and DevOps. Comfortable wearing multiple hats at early-stage startups. Currently at a Seed-stage B2B SaaS company building the entire infrastructure — from Postgres schema to GitHub Actions pipeline to Next.js dashboard.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Next.js", "Docker", "GitHub Actions", "Redis", "TypeScript"],
        "experience_years": 3.0,
        "linkedin_url": "https://linkedin.com/in/nitin-agarwal-generalist",
        "github_url": "https://github.com/nitin-builds",
        "website_url": "https://nitinagarwal.in",
        "projects": [
            {"name": "B2B SaaS Infra from Scratch", "description": "Built entire stack solo at seed-stage startup: FastAPI + PostgreSQL + Next.js + GitHub Actions + Docker Swarm.", "link": ""},
            {"name": "startup-infra-template", "description": "Zero-to-production template for solo founders: Docker Compose, CI, env management, and Slack alerting.", "link": "https://github.com/nitin-builds/startup-infra"},
        ],
    },
    {
        "name": "Anisha Dubey",
        "summary": "Founding engineer with 5 years experience, having been the 1st-5th engineer at 3 startups. Expert at rapidly building and scaling MVPs — from 0 to 50k users. Comfortable with React, Node.js, Python, and AWS. Currently looking for a senior IC or early-stage role where technical breadth matters.",
        "skills": ["React", "Node.js", "Python", "AWS", "PostgreSQL", "Docker", "TypeScript", "Stripe"],
        "experience_years": 5.0,
        "linkedin_url": "https://linkedin.com/in/anisha-dubey-founding",
        "github_url": "https://github.com/anisha-startup",
        "website_url": "https://anishadubey.com",
        "projects": [
            {"name": "EdTech MVP (0 → 50k users)", "description": "Built complete React + Node.js + PostgreSQL LMS from scratch in 6 weeks. Scaled to 50k users in 4 months.", "link": ""},
            {"name": "stripe-india-webhooks", "description": "Stripe webhook handler with Indian GST invoice generation, reconciliation, and UPI payment fallback.", "link": "https://github.com/anisha-startup/stripe-india"},
        ],
    },
    {
        "name": "Jay Mehta",
        "summary": "Blockchain and Web3 engineer with 2.5 years building DeFi protocols and smart contracts on Ethereum and Solana. Expert in Solidity, Rust (Anchor), and DeFi security. Built a DEX aggregator on Polygon that processed $12M in volume in its first month with zero security incidents.",
        "skills": ["Solidity", "Rust", "Anchor", "Ethereum", "Solana", "Hardhat", "The Graph", "ethers.js"],
        "experience_years": 2.5,
        "linkedin_url": "https://linkedin.com/in/jay-mehta-web3",
        "github_url": "https://github.com/jay-blockchain",
        "website_url": "https://jaymehta.xyz",
        "projects": [
            {"name": "Polygon DEX Aggregator", "description": "Solidity DEX aggregator routing across Uniswap V3, Curve, and Balancer. $12M volume month 1, 0 exploits.", "link": "https://github.com/jay-blockchain/polygon-dex-agg"},
            {"name": "solidity-security-checklist", "description": "Automated Slither + Mythril security checklist for Solidity contracts as a GitHub Action. 500+ stars.", "link": "https://github.com/jay-blockchain/solidity-sec-check"},
        ],
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR
# ──────────────────────────────────────────────────────────────────────────────

def generate_resume_pdf(candidate: dict, output_path: Path):
    """Generates a clean single-page PDF resume for a candidate."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    def section_header(title):
        nonlocal y
        y -= 14
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.1, 0.5)
        c.drawString(margin, y, title.upper())
        y -= 4
        c.setStrokeColorRGB(0.1, 0.1, 0.5)
        c.setLineWidth(0.5)
        c.line(margin, y, width - margin, y)
        y -= 12
        c.setFillColorRGB(0, 0, 0)

    def draw_wrapped(text, x, max_width=480, size=10, line_height=14):
        nonlocal y
        c.setFont("Helvetica", size)
        c.setFillColorRGB(0.15, 0.15, 0.15)
        words = text.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if c.stringWidth(test, "Helvetica", size) < max_width:
                line = test
            else:
                c.drawString(x, y, line)
                y -= line_height
                line = word
        if line:
            c.drawString(x, y, line)
            y -= line_height

    # Name
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.05, 0.05, 0.3)
    c.drawString(margin, y, candidate["name"])
    y -= 18

    # Contact
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    links = [l for l in [candidate.get("linkedin_url"), candidate.get("github_url"), candidate.get("website_url")] if l]
    c.drawString(margin, y, "  |  ".join(links[:3]))
    y -= 20

    section_header("Professional Summary")
    draw_wrapped(candidate["summary"], margin)
    y -= 4

    section_header("Technical Skills")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawString(margin, y, "  •  ".join(candidate["skills"]))
    y -= 8

    section_header("Experience")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawString(margin, y, "{} years of professional experience".format(candidate["experience_years"]))
    y -= 16

    section_header("Projects")
    for proj in candidate.get("projects", []):
        if y < 80:
            break
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.05, 0.05, 0.3)
        c.drawString(margin, y, proj["name"])
        y -= 14
        draw_wrapped(proj.get("description", ""), margin + 10, max_width=460)
        y -= 4

    c.save()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

async def seed():
    print("\n🦋 TwinlyAI Demo Candidate Seeder — 50 Candidates")
    print("=" * 55)

    # Find or create system user
    system_user = await users_collection.find_one({"email": "demo@twinlyai.system"})
    if not system_user:
        print("📝 Creating system demo user...")
        result = await users_collection.insert_one({
            "email": "demo@twinlyai.system",
            "role": "candidate",
            "hashed_password": "not-a-real-password",
            "name": "TwinlyAI Demo System",
        })
        user_id = str(result.inserted_id)
    else:
        user_id = str(system_user["_id"])
    print(f"✅ System user: {user_id}")

    # Delete existing bots
    existing = await bots_collection.count_documents({})
    if existing > 0:
        print(f"\n🗑️  Deleting {existing} existing bot records...")
        await bots_collection.delete_many({})
        print("✅ Cleared.")

    # PDF dir
    pdf_dir = Path("data") / "seeded_resumes"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🌱 Seeding {len(CANDIDATES)} candidates...\n")
    global_index = GlobalRecruiterIndex()
    success = 0

    for i, cand in enumerate(CANDIDATES, 1):
        print(f"  [{i:02d}/{len(CANDIDATES)}] {cand['name']:<28}", end=" ", flush=True)

        # MongoDB insert
        bot_doc = {
            "user_id": user_id,
            "name": cand["name"],
            "summary": cand["summary"],
            "skills": cand["skills"],
            "experience_years": cand["experience_years"],
            "linkedin_url": cand.get("linkedin_url", ""),
            "github_url": cand.get("github_url", ""),
            "twitter_url": cand.get("twitter_url", ""),
            "website_url": cand.get("website_url", ""),
            "projects": [
                {"name": p["name"], "description": p["description"], "link": p.get("link", "")}
                for p in cand.get("projects", [])
            ],
        }
        result = await bots_collection.insert_one(bot_doc)
        bot_id = str(result.inserted_id)

        # Generate PDF
        pdf_path = pdf_dir / f"{bot_id}.pdf"
        generate_resume_pdf(cand, pdf_path)

        # Qdrant per-bot indexing
        try:
            pipeline = RAGPipeline(bot_id=bot_id, user_id=user_id, bot_name=cand["name"])
            pipeline.process_file(str(pdf_path))
            qdrant_ok = True
        except Exception as e:
            qdrant_ok = False

        # Global search index
        profile_text = (
            f"Candidate Name: {cand['name']}\n"
            f"Professional Summary: {cand['summary']}\n"
            f"Top Skills: {', '.join(cand['skills'])}\n"
            f"Experience: {cand['experience_years']} years."
        )
        try:
            global_index.add_candidate_profile(bot_id=bot_id, profile_text=profile_text)
            global_ok = True
        except Exception:
            global_ok = False

        status = f"{'✅' if qdrant_ok else '⚠️'} RAG  {'✅' if global_ok else '⚠️'} Search"
        print(status)
        if qdrant_ok and global_ok:
            success += 1

    final = await bots_collection.count_documents({})
    print("\n" + "=" * 55)
    print(f"✅ DONE — {final} candidates seeded ({success} fully indexed)")
    print(f"📁 PDFs: {pdf_dir.resolve()}")
    print("\nRecruiter dashboard and semantic search are now ready.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    asyncio.run(seed())
