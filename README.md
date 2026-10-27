# 🤖 Autonomous Personal Task Agent — v2.0.0

A production-ready, research-grade **Autonomous Personal Task Agent** that transforms Large Language Models from passive conversational systems into **state-based autonomous agents** capable of:

- Understanding natural-language goals with a custom-trained ML intent classifier (**97.25% accuracy**)
- Planning and executing multi-step tool workflows via a **LangGraph cyclic state graph**
- Maintaining short-term & long-term vector memory (**ChromaDB + SQLite**)
- Recovering autonomously from tool failures (up to 3 retries with modified strategies)
- Enforcing human approval before every sensitive action (zero unsafe executions)

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **ML Intent Classifier** | Custom-trained on 1,500 prompts across 15 intents; 97.25% test accuracy |
| **LangGraph State Graph** | Cyclic state machine: `understand_goal → create_plan → select_tool → approval_gate → execute_tool → evaluate_result → update_memory → finalize` |
| **Dual Memory Layer** | ChromaDB vector store for semantic retrieval + SQLite for structured metadata |
| **Human-in-the-Loop Gate** | Pauses execution before `send_email`, `delete_task`, `delete_memory` |
| **Failure Recovery** | Auto-retry up to 3× with modified tool parameters on failure |
| **Tool Registry** | 6 pluggable tools: Web Search, Task Manager, Scheduler, Calendar, Email, Memory |
| **FastAPI Backend** | Async REST API with Server-Sent Events (SSE) streaming |
| **Streamlit UI** | Dark-mode glassmorphic frontend with live execution trace timeline |
| **Benchmark Suite** | 5 research experiments comparing 3 architectural paradigms |

---

## 📁 Repository Structure

```
Ml Project/
├── config/                  # Global configuration & environment settings
│   └── settings.py          # Pydantic-settings v2 config (env / .env)
├── data/                    # Dataset generator, cleaner, splitter (70/15/15)
│   ├── dataset_generator.py
│   ├── clean_dataset.py
│   └── split_dataset.py
├── db/                      # SQLite database, ORM models & CRUD functions
│   ├── database.py          # NativeDB + SQLAlchemy dual-backend
│   ├── models.py
│   ├── schemas.py
│   └── crud.py
├── memory/                  # Short-term state & ChromaDB vector store
│   ├── short_term.py
│   ├── long_term.py
│   └── memory_manager.py
├── tools/                   # BaseTool, ToolRegistry & all tool implementations
│   ├── base.py              # ToolResult + BaseTool abstract class
│   ├── registry.py          # Singleton ToolRegistry
│   ├── web_search.py        # DuckDuckGo + mock fallback
│   ├── task_manager.py
│   ├── scheduler.py         # APScheduler background reminders
│   ├── calendar_tool.py
│   ├── email_tool.py        # Human-approved email sender
│   └── memory_tool.py
├── agent/                   # LangGraph Agent state machine
│   ├── state.py             # AgentState TypedDict (fully documented)
│   ├── nodes.py             # 8 node functions with full logging
│   ├── edges.py             # 3 conditional routing functions
│   └── graph.py             # build_agent_graph() + NativeStateGraph fallback
├── api/                     # FastAPI backend with SSE streaming
│   ├── main.py
│   ├── schemas.py
│   └── routers/
│       ├── agent.py
│       ├── tasks.py
│       └── memory.py
├── ui/                      # Streamlit glassmorphic application
│   ├── app.py               # 4-tab UI with trace timeline & metric cards
│   └── components.py        # CSS design system + rendering helpers
├── evaluation/              # Benchmark dataset & research experiment runner
│   ├── benchmark_dataset.json
│   ├── baselines.py
│   └── run_experiments.py
├── models/                  # ML classifiers & evaluation
│   ├── baseline_classifier.py
│   ├── transformer_classifier.py
│   ├── train.py
│   └── evaluate_ml.py
├── tests/                   # Automated unit & integration tests
│   ├── test_tools.py
│   ├── test_agent.py
│   ├── test_ml.py
│   └── test_api.py
├── docs/                    # Architecture, ER diagram, Flowcharts, Report
│   ├── ARCHITECTURE.md
│   ├── ER_DIAGRAM.md
│   ├── FLOWCHARTS.md
│   ├── EXPERIMENTS.md
│   ├── REPORT.md
│   └── PRESENTATION.md
├── requirements.txt         # Project dependencies (fully versioned)
├── run_tests.py             # Custom test runner
├── run.py                   # Master CLI launcher
└── README.md
```

---

## 🚀 Quickstart

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Environment (optional)

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here   # optional
USE_MOCK_LLM=false
LOG_LEVEL=INFO
```

### 3. Launch Commands

| Command | Description |
|---|---|
| `python run.py --ui` | Start Streamlit UI on http://localhost:8501 |
| `python run.py --api` | Start FastAPI backend on http://localhost:8000 |
| `python run.py --all` | Start **both** API + UI simultaneously |
| `python run.py --train` | Generate dataset and train ML intent classifiers |
| `python run.py --test` | Run the full automated test suite |
| `python run.py --eval` | Run research benchmark experiments |

---

## 🔁 Agent State Machine

```
[User Goal]
     │
     ▼
understand_goal  ──→  create_plan  ──→  select_tool
                                              │
                                    ┌─────────┴──────────┐
                                    │                    │
                             approval_gate         execute_tool ◄──(retry)
                                    │                    │
                              ┌─────┴──────┐       evaluate_result
                           pause      execute_tool       │
                         (await)           │      ┌──────┴──────┐
                                           │   select_tool  update_memory
                                           └──────────────────────│
                                                               finalize
                                                                   │
                                                               [Output]
```

---

## 🧪 Empirical Evaluation Summary

| Architecture Paradigm | Task Completion | Multi-Step | Human Safety | Failure Recovery |
|---|---|---|---|---|
| **Baseline 1: LLM Chatbot (no tools)** | 0.0% | ❌ | ❌ | ❌ |
| **Baseline 2: LLM + Direct Tools (no graph)** | 66.7% | ⚠️ Limited | ❌ | ❌ |
| **Proposed: LangGraph Autonomous Agent** | **100.0%** | ✅ Full cyclic | ✅ Approval gate | ✅ Auto-retry |

---

## 📚 Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and component design |
| [ER_DIAGRAM.md](docs/ER_DIAGRAM.md) | Database entity-relationship diagram |
| [FLOWCHARTS.md](docs/FLOWCHARTS.md) | Agent execution flowcharts |
| [EXPERIMENTS.md](docs/EXPERIMENTS.md) | Detailed benchmark methodology |
| [REPORT.md](docs/REPORT.md) | Full academic research report |
| [PRESENTATION.md](docs/PRESENTATION.md) | Executive presentation deck |

---

## 🔄 Changelog

### v2.0.0 (Oct 2026)
- **Settings**: Upgraded to `pydantic-settings` v2 with `SettingsConfigDict`; added `LOG_LEVEL`, `CHROMA_COLLECTION_NAME`
- **Agent State**: Added `intent_confidence` field; full field documentation
- **Nodes**: Structured logging throughout; `INTENT_PLAN_MAP` constant; smart email recipient extraction; robust try/except on all external calls
- **Edges**: Detailed routing docstrings; logging on every branch
- **Graph**: Safety iteration cap (50) in NativeStateGraph; module docstring
- **BaseTool**: `perf_counter` timing; `tool_name` in `ToolResult`; traceback logging
- **ToolRegistry**: Duplicate-registration warning; `tool_names` property; `__len__`/`__repr__`
- **WebSearch**: `source` field in results; expanded 5-template mock corpus; `ge/le` validation
- **API**: Logging configuration; router prefixes; removed legacy Starlette monkey-patch
- **UI Components**: New hero banner with accent line + feature badges; vertical trace timeline with connector dots; metric cards; memory item cards; full Streamlit widget theming; JetBrains Mono font
- **UI App**: Metric rows in all tabs; status-aware approval gate (JSON preview); experiment cards; disabled execute button when empty; sidebar description panel
- **run.py**: ASCII banner; `--all` flag (API + UI concurrently); extracted helper functions
- **requirements.txt**: All dependencies updated to latest stable; added `plotly`, `pydantic-settings`, `pytest-asyncio`, `python-multipart`
