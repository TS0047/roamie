# ✈️ Roamie — Multi-Agent Travel Planner

> A proof-of-concept travel assistant built from cooperating AI agents — each an expert in one part of the trip.

Roamie explores **multi-agent orchestration**: instead of one monolithic model, the trip is split across specialized agents that each own a domain — sightseeing, dining, and flights — and expose their skills as callable tools. It's built on [**smolagents**](https://github.com/huggingface/smolagents) with HuggingFace inference models.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![smolagents](https://img.shields.io/badge/smolagents-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)

---

## The Agents

| Agent | File | What it does |
|-------|------|--------------|
| 🗺️ **Travel Guide** | `travel_guide.py` | Recommends activities and sights based on destination + interests (history / food / adventure) |
| 🍽️ **Restaurant Guide** | `restaurant.py` | Suggests notable restaurants for a given city |
| 🛫 **Flight Search** | `flight_booking.py` | Parses a natural-language flight query and returns matching options |

Each agent is a `CodeAgent` with a single focused `@tool`, designed so its string output can be consumed by another agent — the foundation for chaining them into a full itinerary planner.

---

## Notable Engineering

The **flight agent** shows the most depth:
- **LLM-first parsing with graceful fallback** — tries a HuggingFace model to extract `origin`, `destination`, `dates`, and `passengers` from free text; if no API key or the call fails, falls back to a **regex parser** so it always works offline
- **Tool-call adapter** (`call_tool`) that transparently handles LangChain `StructuredTool`, `.func`, `.run`, or plain callables
- Structured JSON results ready for downstream agents

---

## Setup

```bash
pip install smolagents langchain requests

# Optional — enables LLM-powered query parsing & recommendations
export HF_API_KEY="your_huggingface_token"
export HF_MODEL="google/flan-t5-small"   # optional override
```

## Run

```bash
# Flight search demo
python flight_booking.py

# Or call an agent directly
python -c "from travel_guide import travel_guide_bot; print(travel_guide_bot('Things to do in Tokyo, I love history'))"
```

---

## Status & Roadmap

This is an early prototype — recommendation data is currently curated/mocked while the agent-orchestration layer is built out.

- [ ] **Orchestrator agent** that chains guide → restaurant → flights into one itinerary
- [ ] Replace mocked recommendation tables with live APIs (Places, flight search)
- [ ] Conversational memory across the planning session
- [ ] Web UI
