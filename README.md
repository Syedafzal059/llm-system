# LLM System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-grade LLM orchestration API** — a mini OpenAI-like backend with intelligent routing, cost-aware model selection, and extensible architecture for caching, fallback, and usage tracking.

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

This system exposes a **unified API** for text generation while abstracting multiple underlying LLM providers. It routes requests based on prompt complexity — simple prompts go to cheaper models, complex ones to stronger models — reducing cost without sacrificing quality.

| Capability | Description |
|------------|-------------|
| **Smart routing** | Route by prompt length/complexity; threshold-based model selection |
| **Unified API** | Single `/generate` endpoint regardless of backend model |
| **Async-first** | Non-blocking I/O for high throughput |
| **Extensible** | Clean service layer for caching, fallback, usage tracking |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│   Router    │
└─────────────┘     │  API Layer  │     └──────┬──────┘
                    └─────────────┘            │
                                               │
                         ┌─────────────────────┴─────────────────────┐
                         ▼                                           ▼
                  ┌─────────────┐                            ┌─────────────┐
                  │ Cheap Model │                            │ Expensive   │
                  │ (< 50 chars)│                            │ Model       │
                  └─────────────┘                            └─────────────┘
```

**Request flow:**

1. **API Layer** — Validates request, applies middleware
2. **Router** — Classifies prompt (length-based heuristic), selects model
3. **Model Layer** — Invokes appropriate model (currently simulated; OpenAI/Anthropic-ready)

---

## Features

- [x] FastAPI with async handlers
- [x] Pydantic request/response validation
- [x] Model routing by prompt length (configurable threshold)
- [x] Health check endpoint
- [ ] Caching (Redis) — *planned*
- [ ] Fallback chain — *planned*
- [ ] Usage tracking — *planned*
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

Generate text from a prompt. The router selects the model based on prompt length.

**Request:**

```json
{
  "prompt": "What is the capital of France?"
}
```

**Response:**

```json
{
  "response": "[Cheap Model] What is the capital of France?"
}
```

**Routing rules:**

- `len(prompt) < 50` → Cheap model
- `len(prompt) >= 50` → Expensive model

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
│   ├── main.py              # FastAPI app entrypoint
│   ├── routes/
│   │   ├── __init__.py
│   │   └── generate.py      # /generate endpoint
│   └── services/
│       ├── models.py        # Model simulations (replace with OpenAI/Anthropic)
│       └── router.py        # Model selection logic
├── requirements.txt
├── PLAN.md                  # Full execution roadmap
└── README.md
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (when integrated) | — |
| `ANTHROPIC_API_KEY` | Anthropic key (when integrated) | — |
| `ROUTER_THRESHOLD` | Prompt length threshold for routing | 50 |

---

## Roadmap

See [PLAN.md](./PLAN.md) for the full implementation roadmap:

- **Phase 1** — ✅ Basic FastAPI + routing
- **Phase 2** — Caching (in-memory → Redis)
- **Phase 3** — Fallback & retry
- **Phase 4** — Usage tracking
- **Phase 5** — Async, streaming, Docker

---

## License

MIT
