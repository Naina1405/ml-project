# Autonomous Personal Task Agent Architecture Specification

## 1. System Overview

The **Autonomous Personal Task Agent** transforms standard Large Language Model (LLM) conversational interfaces into a goal-driven, autonomous task execution system. The architecture features:

- **ML Intent Classifier**: Custom-trained model (TF-IDF + Logistic Regression Baseline vs Transformer Embedding MLP Classifier) for intent and tool requirement prediction.
- **LangGraph State Graph**: Cyclic state machine orchestrating goal understanding, planning, tool selection, human approval gates, execution, failure evaluation, and memory persistence.
- **Dual Memory Layer**: Short-Term state memory (transient task state) + Long-Term persistent memory (ChromaDB vector store + SQLite metadata).
- **Human-in-the-Loop Safety Gate**: Interactive approval pause before executing sensitive tools like `send_email`.
- **FastAPI & Streamlit**: Asynchronous REST backend with SSE streaming execution trace and a dark-mode Streamlit UI.

---

## 2. LangGraph State Machine Diagram

```mermaid
graph TD
    A[User Natural Language Goal] --> B[understand_goal]
    B --> C[create_plan]
    C --> D[select_tool]
    
    D -->|Requires Approval? YES| E[approval_gate]
    D -->|Requires Approval? NO| F[execute_tool]
    D -->|No Tools / Complete| H[update_memory]
    
    E -->|User Approved| F
    E -->|User Rejected| I[finalize]
    
    F --> G[evaluate_result]
    G -->|Success & More Steps| D
    G -->|Failure & Retry < 3| D
    G -->|Max Retries Exceeded| I
    G -->|All Steps Complete| H
    
    H --> I
    I --> J[End / Final Report]
```

---

## 3. Core Component Modules

| Module | File Location | Responsibility |
|---|---|---|
| **Data & ML** | `data/`, `models/` | Synthetic task dataset generation, cleaning, 70/15/15 splitting, baseline & embedding model training & evaluation. |
| **Database** | `db/` | SQLite database, schema migrations, CRUD helper functions for `users`, `tasks`, `task_steps`, `memories`. |
| **Memory** | `memory/` | Short-term state scratchpad & ChromaDB vector embedding long-term memory store. |
| **Tools** | `tools/` | Standardized `BaseTool` interface, `ToolRegistry`, Web Search, Task Manager, APScheduler, Calendar, Email, Memory tools. |
| **Agent Core** | `agent/` | Pydantic/TypedDict `AgentState`, graph nodes, conditional routing edges, LangGraph/Native compiled workflow graph. |
| **API Backend** | `api/` | FastAPI server endpoints (`/agent/run`, `/agent/approve`, `/tasks`, `/memory`) with Server-Sent Events. |
| **UI** | `ui/` | Glassmorphic Streamlit frontend with real-time execution trace visualization, interactive approval dialogs, and benchmark lab. |
