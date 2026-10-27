# Executive Presentation: Autonomous Personal Task Agent

## Slide 1: Title & Project Overview
- **Title**: Autonomous Personal Task Agent Using LLMs and Tool Calling
- **Objective**: Transforming passive LLM chatbots into autonomous, stateful task execution agents.
- **Key Stack**: Python 3.x, LangGraph, FastAPI, Streamlit, ChromaDB, SQLite, APScheduler, scikit-learn, SentenceTransformers.

---

## Slide 2: Core Problem Statement
- Traditional chatbots only generate conversational text; they cannot execute real-world tasks.
- Lack of multi-step planning, state tracking, external tool invocation, memory, and failure recovery.
- High risk of unauthorized side-effects (e.g. sending emails or deleting records without user consent).

---

## Slide 3: High-Level Architecture
- **Natural Language Goal** -> **ML Intent Classifier** -> **Task Planner & Decomposition** -> **Tool Selection** -> **Human Approval Gate** -> **Tool Execution** -> **Result Evaluation & Retry** -> **ChromaDB Memory Update** -> **Final Summary Report**.

---

## Slide 4: Machine Learning Intent Classification
- Custom dataset of **1,500 realistic task prompts** across **15 intent categories**.
- 70% Train / 15% Val / 15% Test split.
- Baseline (TF-IDF + Logistic Regression) vs Advanced Embedding MLP Head: **97.25% Classification Accuracy**.

---

## Slide 5: LangGraph Cyclic Orchestration & Tool Registry
- Standardized tool interface with Pydantic input/output schemas.
- 6 Integrated Tools: Web Search, Task Manager, APScheduler Reminder, Calendar, Email Drafter/Sender, Memory Store.
- State-based cyclic flow supporting multi-step goal execution.

---

## Slide 6: Human-in-the-Loop Safety & Failure Recovery
- **Interactive Approval Gate**: Automatically pauses execution on sensitive actions (`send_email`, `delete_task`).
- **Autonomous Failure Recovery**: Up to 3 automatic retries with query/parameter reformulation upon tool failure.

---

## Slide 7: Dual Memory Architecture
- **Short-Term Memory**: Transient state scratchpad and execution trace inside `AgentState`.
- **Long-Term Memory**: ChromaDB vector store + SQLite metadata for semantic preference retrieval.

---

## Slide 8: Empirical Benchmark Results
- **Task Completion Rate**:
  - Baseline 1 (LLM Chatbot): **0.0%**
  - Baseline 2 (LLM + Direct Tools): **66.7%**
  - **Proposed System (LangGraph Agent)**: **100.0%**
- **Safety Compliance**: **100% (0 unauthorized sensitive executions)**.

---

## Slide 9: Demo & User Interfaces
- **FastAPI Asynchronous Backend**: REST endpoints with SSE real-time streaming trace.
- **Streamlit Glassmorphic UI**: Interactive Chat, Real-time Timeline Trace, Approval Popups, Memory Dashboard, and Benchmark Lab.
