# LLM System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-grade LLM orchestration API** — a mini OpenAI-like backend with intelligent routing, in-memory caching, retry with fallback, and usage tracking.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

This system exposes a **unified API** for text generation while abstracting multiple underlying LLM providers. It routes requests based on prompt complexity, caches responses, retries on failure, and falls back to a backup model — reducing cost and improving reliability.

| Capability | Description |
|------------|-------------|
| **Smart routing** | Route by prompt length; simple prompts → cheap model, complex → expensive |
| **In-memory caching** | Skip redundant model calls for repeated prompts |
| **Retry + fallback** | 2 retries on primary failure, then fallback to cheap model |
| **Usage tracking** | Log every request to CSV (timestamp, user, model, tokens, duration) |
| **Unified API** | Single `/generate` endpoint regardless of backend |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│   Router    │
└─────────────┘     │  API Layer  │     └──────┬──────┘
                    └─────────────┘            │
                                               │
                     ┌─────────────────────────┴─────────────────────────┐
                     │                                                   │
                     ▼                                                   │
              ┌─────────────┐                                     ┌──────┴──────┐
              │   Cache     │   HIT → return                       │  Model      │
              │  (in-memory)│   MISS → continue                   │  Layer      │
              └──────┬──────┘                                     └──────┬──────┘
                     │                                                   │
                     └───────────────────────────────────────────────────┘
                                               │
                     ┌─────────────────────────┴─────────────────────────┐
                     ▼                                                   ▼
              ┌─────────────┐                                     ┌─────────────┐
              │ Cheap Model │                                     │ Expensive   │
              │ (< 50 chars)│                                    │ Model       │
              └──────┬──────┘                                     └──────┬──────┘
                     │                                                   │
                     │  Primary fails (2 retries)                        │
                     └───────────────────────┬───────────────────────────┘
                                             ▼
                                    ┌─────────────┐
                                    │  Fallback   │
                                    │  (cheap)    │
                                    └─────────────┘
                                             │
                                             ▼
                                    ┌─────────────┐
                                    │Usage Logger │
                                    │  (CSV)      │
                                    └─────────────┘
```

**Request flow:**

1. **API Layer** — Validates request
2. **Router** — Check cache → HIT: return cached; MISS: continue
3. **Router** — Select primary model (cheap vs expensive by length)
4. **Router** — Try primary (2 retries with 0.5s delay)
5. **Router** — On failure: call fallback model
6. **Router** — Store in cache, log usage to CSV

---

## Features

- [x] FastAPI with async handlers
- [x] Pydantic request/response validation
- [x] Model routing by prompt length (threshold: 50 chars)
- [x] In-memory caching
- [x] Retry with exponential backoff (2 attempts)
- [x] Fallback chain (cheap model as fallback)
- [x] Usage tracking (CSV logging)
- [x] Health check endpoint
- [ ] Redis caching — *planned*
- [ ] Streaming — *planned*

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Install

```bash
git clone https://github.com/Syedafzal059/llm-system.git
cd llm-system
pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: **http://localhost:8000/docs**

---

## API Reference

### `POST /generate/`

Generate text from a prompt. Uses cache when available; otherwise routes to model with retry and fallback.

**Request:**

```json
{
  "prompt": "What is the capital of France?"
}
```

**Response (cache miss, cheap model):**

```json
{
  "response": "[Cheap Model] What is the capital of France?"
}
```

**Response (cache hit):**

```json
{
  "response": "[Cached][Cheap Model] What is the capital of France?"
}
```

**Response (fallback used):**

```json
{
  "response": "[Fallback] [Cheap Model] ..."
}
```

**Routing rules:**

- `len(prompt) < 50` → Cheap model
- `len(prompt) >= 50` → Expensive model
- Primary failure after 2 retries → Fallback (cheap)

### `GET /health`

Health check for load balancers and monitoring.

**Response:**

```json
{
  "status": "I am healthy :)"
}
```

---

## Project Structure

```
llm-system/
├── app/
│   ├── main.py                   # FastAPI app entrypoint
│   ├── routes/
│   │   ├── __init__.py
│   │   └── generate.py           # /generate endpoint
│   ├── services/
│   │   ├── models.py             # cheap_model, expensive_model (simulated)
│   │   ├── router.py             # Routing + cache + retry + fallback
│   │   └── fallback.py           # fallback_model
│   └── utils/
│       ├── cache.py              # InMemoryCache
│       └── file_usage_tracker.py  # CSV usage logging
├── requirements.txt
└── README.md
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (when integrated) | — |
| `ANTHROPIC_API_KEY` | Anthropic key (when integrated) | — |
| `ROUTER_THRESHOLD` | Prompt length threshold for routing | 50 |
| `USAGE_LOG_FILE` | Path for usage CSV | `usage.csv` |

---

## Roadmap

- **Phase 1** — ✅ Basic FastAPI + routing
- **Phase 2** — ✅ In-memory caching
- **Phase 3** — ✅ Retry + fallback chain
- **Phase 4** — ✅ Usage tracking (CSV)
- **Phase 5** — Redis cache, streaming, Docker — *planned*

---

## License

MIT
