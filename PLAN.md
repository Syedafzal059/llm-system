# LLM System — Production Execution Plan

> A step-by-step blueprint for building a mini OpenAI-like backend with routing, caching, fallback, and usage tracking.

---

## 1. PROJECT OVERVIEW

### What We Are Building

A **production-grade LLM orchestration backend** that exposes a unified API to generate text while intelligently managing multiple underlying models. The system routes requests to cost-appropriate models, caches responses, handles failures with fallbacks, and tracks usage for billing and analytics.

**Core capabilities:**

- **Unified API** — Single `/generate` endpoint regardless of underlying model
- **Smart routing** — Route simple prompts to cheaper models, complex ones to stronger models
- **Caching** — Avoid redundant API calls for repeated or near-duplicate prompts
- **Fallback & retry** — Graceful degradation when primary model fails
- **Usage tracking** — Token counts, latency, and cost attribution per request

### Real-World Analogy

Like **OpenAI’s API** or **Anthropic’s Claude API**: clients send prompts to one endpoint and receive completions. Internally, the system chooses which model to call, reuses cached answers, and handles outages. This plan builds the same core machinery at a smaller scale.

### Key Capabilities

| Capability        | Purpose                                         |
|-------------------|--------------------------------------------------|
| Multi-model routing | Route by complexity/context to control cost     |
| Response caching   | Cut latency and cost for repeated prompts       |
| Fallback chain     | Failover to backup models on errors             |
| Usage logging      | Token usage, latency, and cost per request      |
| Async processing   | High throughput with minimal threads/processes  |
| Streaming (future) | Token-by-token responses for better UX          |

---

## 2. SYSTEM ARCHITECTURE

### High-Level Architecture Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  API Layer  │────▶│   Router    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                      ┌────────────────────────┼────────────────────────┐
                      │                        │                        │
                      ▼                        ▼                        ▼
               ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
               │   Cache     │          │   Model     │          │   Usage     │
               │  (Redis)    │          │   Layer     │          │   Tracker   │
               └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
                      │                        │                        │
                      │   MISS                 │                        │
                      └───────────────────────▶│                        │
                                               │   LLM APIs             │
                                               │ (OpenAI, Anthropic…)   │
                                               └───────────────────────┘
```

### End-to-End Flow

```
Client Request
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. API Layer                                                             │
│    - Validate request (prompt, params)                                   │
│    - Auth/API key validation                                             │
│    - Rate limiting (future)                                              │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. Router                                                                │
│    - Classify prompt (simple vs complex)                                 │
│    - Select model: cheap (e.g. gpt-3.5) vs expensive (e.g. gpt-4)        │
│    - Build model chain for fallback                                      │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Cache                                                                 │
│    - Hash prompt + params                                                │
│    - Check Redis for cached response                                     │
│    - HIT → return cached; MISS → continue                                │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Model Layer                                                           │
│    - Call selected provider (OpenAI, Anthropic, etc.)                    │
│    - On failure → retry → fallback to next model in chain                │
│    - Parse response, extract tokens                                      │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. Usage Tracker                                                         │
│    - Log: prompt tokens, completion tokens, latency, model, cost         │
│    - Write to DB or log stream                                           │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
   Response to Client
```

### Component Descriptions

| Component     | Responsibility                                                                 |
|---------------|---------------------------------------------------------------------------------|
| **API Layer** | HTTP entrypoint; validation; auth; request/response handling; error mapping    |
| **Router**    | Prompt classification; model selection; fallback chain ordering                |
| **Cache**     | Key generation from prompt+params; get/set in Redis; TTL management             |
| **Model Layer** | Provider abstraction; HTTP calls; retry logic; token extraction from responses |
| **Usage Tracker** | Log tokens, latency, cost; persistence for analytics and billing             |

---

## 3. DIRECTORY STRUCTURE

```
llm_system/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                 # FastAPI app entrypoint
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── generate.py     # /generate endpoint
│   │   │   └── health.py       # /health, /ready probes
│   │   └── dependencies.py     # Dep injection (cache, router, etc.)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings from env vars
│   │   ├── exceptions.py       # Custom API exceptions
│   │   └── security.py        # API key validation
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── router.py           # Model routing logic
│   │   ├── cache.py            # Cache abstraction (memory/Redis)
│   │   ├── model_client.py     # LLM provider calls
│   │   ├── fallback.py         # Retry + fallback orchestration
│   │   └── usage_tracker.py    # Logging usage metrics
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py         # Pydantic request schemas
│   │   └── responses.py        # Pydantic response schemas
│   │
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py          # Cache key from prompt+params
│       └── prompt_analyzer.py  # Simple complexity heuristic
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Central config (can import from app.core.config)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_routes/
│   │   └── test_generate.py
│   ├── test_services/
│   │   ├── test_router.py
│   │   ├── test_cache.py
│   │   └── test_fallback.py
│   └── test_utils/
│       └── test_hashing.py
│
├── scripts/
│   ├── run_dev.py              # Local dev runner
│   └── seed_cache.py           # Optional cache warmup
│
├── .env.example                # Template for required env vars
├── .gitignore
├── Dockerfile                  # Future container
├── docker-compose.yml          # Future: app + Redis
├── pyproject.toml              # Dependencies, lint, test config
├── requirements.txt            # Pinned deps
├── PLAN.md                     # This document
└── README.md
```

### File & Folder Purpose

| Path                    | Purpose                                                                 |
|-------------------------|-------------------------------------------------------------------------|
| `app/main.py`           | FastAPI app, middleware, router registration                            |
| `app/api/routes/`       | HTTP endpoints and request handling                                     |
| `app/api/dependencies.py` | Injected services (cache, router, model client)                       |
| `app/core/config.py`    | Load config from env (`OPENAI_API_KEY`, etc.)                           |
| `app/core/exceptions.py`| Custom exceptions and handlers                                          |
| `app/core/security.py`  | API key validation                                                      |
| `app/services/router.py`| Model selection from prompt/context                                     |
| `app/services/cache.py` | Cache interface; in-memory first, Redis later                           |
| `app/services/model_client.py` | Provider abstraction; calls to OpenAI/Anthropic APIs               |
| `app/services/fallback.py` | Retry and fallback to secondary models                             |
| `app/services/usage_tracker.py` | Record tokens, latency, cost per request                          |
| `app/models/`           | Pydantic schemas for requests and responses                             |
| `app/utils/hashing.py`  | Deterministic cache key from prompt + params                            |
| `app/utils/prompt_analyzer.py` | Heuristics for prompt complexity (e.g. length, structure)        |
| `config/settings.py`    | Centralized configuration                                               |
| `tests/`                | Unit and integration tests                                              |
| `scripts/`               | Dev and ops helpers                                                     |

---

## 4. STEP-BY-STEP IMPLEMENTATION PLAN

### Phase 1: Foundation (Week 1)

**Goal:** Minimal working API.

| Step | What to Build | Why | Outcome |
|------|---------------|-----|---------|
| 1.1 | FastAPI app with `/health` and `/generate` | Provides a stable entrypoint and basic observability | Responding `/health` and single `/generate` route |
| 1.2 | Pydantic schemas for request/response | Typed validation and docs | `GenerateRequest`, `GenerateResponse` schemas |
| 1.3 | Config from env (`pydantic-settings`) | Avoid hardcoded secrets; 12-factor config | `OPENAI_API_KEY` and base URL from env |
| 1.4 | Direct OpenAI call in `/generate` | Prove end-to-end flow | Real completions from GPT-3.5/4 |

**Deliverable:** `POST /generate` returns a completion from a single model.

---

### Phase 2: Routing Logic (Week 2)

**Goal:** Route by complexity to control cost.

| Step | What to Build | Why | Outcome |
|------|---------------|-----|---------|
| 2.1 | `prompt_analyzer.py` — e.g. length, question mark count, structure | Simple heuristic for “simple” vs “complex” | `is_complex_prompt(prompt) -> bool` |
| 2.2 | `router.py` — maps complexity to model IDs | Central logic for model selection | `select_model(prompt) -> str` |
| 2.3 | Wire router into `/generate` | Use routing before calling the model | Cheap model for simple prompts, expensive for complex |

**Heuristic example:** If `len(prompt) < 100` and no multi-step phrasing → use cheap model; else → expensive model.

**Deliverable:** Routing based on prompt complexity.

---

### Phase 3: Caching (Week 3)

**Goal:** Cache responses to reduce cost and latency.

| Step | What to Build | Why | Outcome |
|------|---------------|-----|---------|
| 3.1 | `hashing.py` — SHA-256(prompt + JSON(params)) | Stable, deterministic cache keys | `generate_cache_key(prompt, params) -> str` |
| 3.2 | In-memory cache (dict) with TTL | Quick feedback loop; no external deps | Hit path returns cached response immediately |
| 3.3 | `cache.py` interface (e.g. `get`, `set`) | Abstraction for swapping backends | Easy to replace in-memory with Redis later |
| 3.4 | Redis backend for `cache.py` | Shared cache across instances; production-ready | Redis-backed cache with TTL |

**Deliverable:** Cache layer that reduces repeated calls and is Redis-ready.

---

### Phase 4: Fallback & Retry (Week 4)

**Goal:** Robust error handling and failover.

| Step | What to Build | Why | Outcome |
|------|---------------|-----|---------|
| 4.1 | Retry with exponential backoff for transient errors | Handle rate limits, timeouts, 5xx | Up to 3 retries before fallback |
| 4.2 | `fallback.py` — ordered model chain | Failover path when primary fails | `[primary, secondary, tertiary]` |
| 4.3 | Fallback loop: try models in order until one succeeds | Improve availability | Graceful degradation on provider outages |
| 4.4 | Structured error responses (model failed vs invalid request) | Clear client feedback | Different status codes and messages for different failures |

**Deliverable:** Retry and fallback for model calls.

---

### Phase 5: Usage Tracking (Week 5)

**Goal:** Track tokens and costs per request.

| Step | What to Build | Why | Outcome |
|------|---------------|-----|---------|
| 5.1 | Extract token counts from provider response (e.g. `usage.prompt_tokens`) | Accurate usage data | `prompt_tokens`, `completion_tokens` per request |
| 5.2 | `usage_tracker.py` — log to JSON file or stdout | Simple start; no DB yet | Log line per request with tokens, latency, model |
| 5.3 | Optional: Postgres table for usage | Analytics and billing | Persisted usage records in DB |
| 5.4 | Cost estimation (tokens × price per 1K tokens) | Cost visibility | Approximate cost per request |

**Deliverable:** Logged usage and optional DB persistence.

---

### Phase 6: Advanced (Week 6+)

**Goal:** Production-level performance and UX.

| Step | What to Build | Why | Outcome |
|------|---------------|-----|---------|
| 6.1 | Async model calls (`httpx.AsyncClient`) | Higher concurrency | Non-blocking I/O for more throughput |
| 6.2 | Streaming response (SSE or similar) | Real-time tokens | Stream tokens as they arrive |
| 6.3 | Batch inference endpoint (optional) | Batch multiple prompts in one request | Reduced per-request overhead |
| 6.4 | Dockerfile + docker-compose | Reproducible deployment | App + Redis in containers |

**Deliverable:** Async, streaming, and Docker deployment.

---

## 5. TECH STACK

| Technology | Purpose | Rationale |
|------------|---------|-----------|
| **FastAPI** | Web framework | Async-native, auto docs, Pydantic, high performance |
| **Pydantic / pydantic-settings** | Validation and config | Type-safe request/response and env parsing |
| **httpx** | HTTP client | Async support, timeout control, streaming |
| **Redis** | Response cache | Fast, TTL, shared across instances |
| **Postgres** (optional) | Usage and logs | Persistent storage for analytics and billing |
| **Async Python** | Concurrency | Better throughput without more threads |
| **Docker** | Deployment | Reproducible, portable runtime |
| **pytest + pytest-asyncio** | Testing | Async tests for routes and services |

---

## 6. GITHUB STRUCTURE & STRATEGY

### Repository Layout

- **Root:** README, LICENSE, config files, `PLAN.md`
- **`app/`:** Application code
- **`tests/`:** Tests mirroring `app/` structure
- **`.github/workflows/`:** CI (lint, test, optional build)

### Files to Include

```
.gitignore          # Python, env, IDE, OS
.env.example        # All required env vars (no secrets)
README.md           # From section 7
LICENSE             # MIT or company choice
requirements.txt    # Pinned deps
pyproject.toml      # Optional: tools, packaging
Dockerfile
docker-compose.yml
```

### Commit Strategy

**Milestone-based commits:**

| Milestone | Example message |
|-----------|------------------|
| Phase 1   | `feat: add FastAPI app with /generate and OpenAI integration` |
| Phase 2   | `feat: add prompt-based model routing` |
| Phase 3   | `feat: add in-memory and Redis caching` |
| Phase 4   | `feat: add retry and fallback for model calls` |
| Phase 5   | `feat: add usage tracking and token logging` |
| Phase 6   | `feat: add async handling and streaming` |

**Conventions:**

- `feat:` new feature  
- `fix:` bug fix  
- `refactor:` internal change  
- `test:` tests only  
- `docs:` docs only  

### Branch Strategy

- **`main`** — production-ready
- **`develop`** — integration branch
- **Feature branches** — `feat/routing`, `feat/cache`, etc.
- Merge via PR after tests pass.

### Example Repo Name

```
llm-orchestration-api
llm-gateway
prompt-router
```

---

## 7. README CONTENT TEMPLATE

```markdown
# LLM Orchestration API

Production-grade API for LLM text generation with smart routing, caching, fallback, and usage tracking.

## Architecture

```
Client → API → Router → Cache → Model Layer → Response → Usage Tracker
```

- **Router:** Selects model based on prompt complexity
- **Cache:** Redis-backed response cache
- **Fallback:** Automatic failover to backup models
- **Usage Tracker:** Token and cost logging

## Features

- Unified `/generate` endpoint for multiple LLM providers
- Cost-aware routing (cheap vs expensive models)
- Response caching for repeated prompts
- Retry with exponential backoff + fallback chain
- Usage tracking (tokens, latency, cost)

## Setup

1. **Clone and install:**

   ```bash
   git clone https://github.com/your-org/llm-orchestration-api.git
   cd llm-orchestration-api
   pip install -r requirements.txt
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   # Set OPENAI_API_KEY, optional ANTHROPIC_API_KEY, REDIS_URL
   ```

3. **Run locally:**

   ```bash
   uvicorn app.main:app --reload
   ```

4. **With Docker:**

   ```bash
   docker-compose up -d
   ```

## API Usage

**Generate text:**

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "max_tokens": 100
  }'
```

**Response:**

```json
{
  "text": "The capital of France is Paris.",
  "model": "gpt-3.5-turbo",
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 6,
    "total_tokens": 14
  },
  "cached": false
}
```

## Configuration

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (required) |
| `ANTHROPIC_API_KEY` | Anthropic key (optional, for fallback) |
| `REDIS_URL` | Redis URL (default: in-memory if absent) |
| `LOG_LEVEL` | Logging level |

## License

MIT
```

---

## 8. RESUME BULLETS

- **Designed and implemented a production LLM orchestration API** with intelligent routing (cheap vs expensive models based on prompt complexity), Redis-backed caching, retry/fallback, and usage tracking, reducing average cost by ~40% while improving latency for repeated prompts.

- **Built a multi-model gateway** integrating OpenAI and Anthropic APIs with automatic failover, exponential backoff, and streaming support, handling 500+ concurrent requests via async Python and FastAPI.

- **Architected cost-aware LLM routing and caching** using prompt complexity heuristics and Redis, cutting redundant API calls by 60% for repeated queries and enabling token-level usage tracking for billing and analytics.

---

## 9. INTERVIEW QUESTIONS

| Question | Intended focus |
|----------|-----------------|
| **Why route between models instead of always using the best one?** | Cost vs quality trade-off; use cheap models for simple tasks. |
| **How does your caching work? What’s the cache key?** | Hash of prompt + params; TTL; Redis for production. |
| **What happens when the primary model fails?** | Retry with backoff, then fallback to next model in chain. |
| **How would you scale this to 10K RPS?** | Async, connection pooling, Redis cluster, horizontal scaling, rate limiting. |
| **How do you prevent cache poisoning or adversarial prompts?** | Input validation, sanitization, length limits, optional abuse detection. |
| **How do you measure and optimize latency?** | End-to-end timing, per-component metrics, profiling, async/connection tuning. |
| **What’s the trade-off of in-memory vs Redis cache?** | In-memory: simple, per-process; Redis: shared, durable, suitable for multiple instances. |
| **How would you add a new LLM provider?** | Abstract provider interface; implement adapter; register in routing/fallback config. |
| **Why use async Python for this?** | I/O-bound calls to LLM APIs; async enables high concurrency without many threads. |
| **How do you handle streaming when using a cache?** | Cache full response; on hit, stream cached content to client with same interface. |

---

## 10. FUTURE ENHANCEMENTS

| Enhancement | Description |
|-------------|-------------|
| **Complexity-based model selection** | Embedding similarity or classifier to choose model by actual complexity, not just heuristics |
| **Cost optimization** | A/B test routing rules; tune thresholds using usage data |
| **Quantization / local models** | Run smaller models locally (e.g. Ollama) for very cheap, low-latency paths |
| **Multi-region deployment** | Deploy close to users; region-specific routing; geo-aware failover |
| **Rate limiting per client** | Token bucket or sliding window per API key |
| **Prompt injection detection** | Simple detectors to block or re-route suspicious prompts |
| **Observability** | OpenTelemetry, traces, and dashboards (e.g. Grafana) |
| **Queue for batch jobs** | Redis/Celery for long-running or batch generation |
| **Fine-tuned routing model** | Train a small model to predict which backbone model to use |
| **Multi-tenancy** | Per-tenant limits, cost caps, and isolation |

---

*Document version: 1.0*
