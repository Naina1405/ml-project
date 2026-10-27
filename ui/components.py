import streamlit as st
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
PALETTE = {
    "bg": "#080c14",
    "surface": "#0f1724",
    "surface2": "#141e2e",
    "border": "rgba(56, 139, 253, 0.15)",
    "text": "#e6edf3",
    "muted": "#7d8590",
    "blue": "#58a6ff",
    "purple": "#bc8cff",
    "green": "#3fb950",
    "amber": "#d29922",
    "red": "#f85149",
    "cyan": "#39d1c7",
}

CUSTOM_CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Global reset ────────────────────────────────────────────────── */
  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    color: {PALETTE['text']};
  }}
  .stApp {{
    background: {PALETTE['bg']};
    background-image:
      radial-gradient(ellipse at 20% 0%, rgba(88,166,255,0.06) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 0%, rgba(188,140,255,0.06) 0%, transparent 60%);
  }}

  /* ── Sidebar ─────────────────────────────────────────────────────── */
  [data-testid="stSidebar"] {{
    background: {PALETTE['surface']} !important;
    border-right: 1px solid {PALETTE['border']};
  }}

  /* ── Header card ─────────────────────────────────────────────────── */
  .hero-card {{
    background: linear-gradient(135deg, rgba(15,23,36,0.95) 0%, rgba(20,30,46,0.95) 100%);
    border: 1px solid {PALETTE['border']};
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 0 40px rgba(88,166,255,0.07), 0 8px 32px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
  }}
  .hero-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {PALETTE['blue']}, {PALETTE['purple']}, {PALETTE['cyan']});
  }}
  .hero-title {{
    margin: 0;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, {PALETTE['blue']} 0%, {PALETTE['purple']} 60%, {PALETTE['cyan']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
  }}
  .hero-subtitle {{
    margin-top: 8px;
    color: {PALETTE['muted']};
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
  }}
  .hero-badges {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 14px;
  }}
  .hero-badge {{
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.3px;
  }}

  /* ── Glass cards ─────────────────────────────────────────────────── */
  .glass-card {{
    background: rgba(15, 23, 36, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid {PALETTE['border']};
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }}
  .glass-card:hover {{
    border-color: rgba(88,166,255,0.3);
    box-shadow: 0 4px 32px rgba(88,166,255,0.08);
  }}

  /* ── Section headers ─────────────────────────────────────────────── */
  .section-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.1rem;
    font-weight: 700;
    color: {PALETTE['text']};
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid {PALETTE['border']};
  }}
  .section-icon {{
    font-size: 1.2rem;
  }}

  /* ── Trace timeline ──────────────────────────────────────────────── */
  .trace-wrapper {{
    display: flex;
    flex-direction: column;
    gap: 0;
    position: relative;
  }}
  .trace-item {{
    display: flex;
    gap: 16px;
    padding: 12px 0;
    position: relative;
  }}
  .trace-dot-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 28px;
    flex-shrink: 0;
  }}
  .trace-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 2px solid {PALETTE['blue']};
    background: {PALETTE['bg']};
    box-shadow: 0 0 8px rgba(88,166,255,0.4);
    z-index: 1;
    flex-shrink: 0;
    margin-top: 4px;
  }}
  .trace-dot.completed  {{ border-color: {PALETTE['green']};  box-shadow: 0 0 8px rgba(63,185,80,0.4); }}
  .trace-dot.waiting    {{ border-color: {PALETTE['amber']};  box-shadow: 0 0 8px rgba(210,153,34,0.4); }}
  .trace-dot.failed     {{ border-color: {PALETTE['red']};    box-shadow: 0 0 8px rgba(248,81,73,0.4); }}
  .trace-dot.retrying   {{ border-color: {PALETTE['cyan']};   box-shadow: 0 0 8px rgba(57,209,199,0.4); }}
  .trace-line {{
    width: 2px;
    background: {PALETTE['border']};
    flex: 1;
    min-height: 20px;
    margin-top: 4px;
  }}
  .trace-content {{
    flex: 1;
    padding-bottom: 8px;
  }}
  .trace-meta {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }}
  .trace-time {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: {PALETTE['muted']};
  }}
  .trace-step-name {{
    font-weight: 600;
    font-size: 0.95rem;
    color: {PALETTE['text']};
  }}
  .trace-details {{
    font-size: 0.875rem;
    color: {PALETTE['muted']};
    line-height: 1.5;
    white-space: pre-wrap;
  }}

  /* ── Status badges ───────────────────────────────────────────────── */
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 20px;
    letter-spacing: 0.4px;
    text-transform: uppercase;
  }}
  .badge-success {{ background: rgba(63,185,80,0.15);  color: {PALETTE['green']}; border: 1px solid rgba(63,185,80,0.35); }}
  .badge-warning {{ background: rgba(210,153,34,0.15); color: {PALETTE['amber']}; border: 1px solid rgba(210,153,34,0.35); }}
  .badge-danger  {{ background: rgba(248,81,73,0.15);  color: {PALETTE['red']};   border: 1px solid rgba(248,81,73,0.35); }}
  .badge-info    {{ background: rgba(88,166,255,0.15); color: {PALETTE['blue']};  border: 1px solid rgba(88,166,255,0.35); }}
  .badge-purple  {{ background: rgba(188,140,255,0.15); color: {PALETTE['purple']}; border: 1px solid rgba(188,140,255,0.35); }}
  .badge-cyan    {{ background: rgba(57,209,199,0.15); color: {PALETTE['cyan']};  border: 1px solid rgba(57,209,199,0.35); }}

  /* ── Metric cards ────────────────────────────────────────────────── */
  .metric-card {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
  }}
  .metric-value {{
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, {PALETTE['blue']}, {PALETTE['purple']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .metric-label {{
    font-size: 0.8rem;
    color: {PALETTE['muted']};
    margin-top: 2px;
    font-weight: 500;
  }}

  /* ── Memory items ────────────────────────────────────────────────── */
  .memory-item {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
  }}
  .memory-item:hover {{ border-color: rgba(88,166,255,0.3); }}
  .memory-content {{ font-size: 0.9rem; color: {PALETTE['text']}; margin-top: 6px; line-height: 1.5; }}
  .memory-meta {{ font-size: 0.75rem; color: {PALETTE['muted']}; margin-top: 4px; }}

  /* ── Streamlit tweaks ────────────────────────────────────────────── */
  .stTextArea textarea, .stTextInput input {{
    background: {PALETTE['surface2']} !important;
    border-color: {PALETTE['border']} !important;
    color: {PALETTE['text']} !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 8px !important;
  }}
  .stSelectbox > div > div {{
    background: {PALETTE['surface2']} !important;
    border-color: {PALETTE['border']} !important;
  }}
  .stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {PALETTE['blue']}, {PALETTE['purple']}) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: opacity 0.2s, transform 0.1s !important;
  }}
  .stButton > button[kind="primary"]:hover {{
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
  }}
  .stButton > button:not([kind="primary"]) {{
    background: {PALETTE['surface2']} !important;
    border: 1px solid {PALETTE['border']} !important;
    color: {PALETTE['text']} !important;
    border-radius: 8px !important;
  }}
  .stTabs [data-baseweb="tab-list"] {{
    background: {PALETTE['surface']} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid {PALETTE['border']} !important;
  }}
  .stTabs [data-baseweb="tab"] {{
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
    color: {PALETTE['muted']} !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(88,166,255,0.2), rgba(188,140,255,0.2)) !important;
    color: {PALETTE['text']} !important;
    border: 1px solid {PALETTE['border']} !important;
  }}
  .stExpander {{
    border: 1px solid {PALETTE['border']} !important;
    border-radius: 10px !important;
    background: {PALETTE['surface2']} !important;
  }}
  .stSpinner > div {{ color: {PALETTE['blue']} !important; }}
  [data-testid="stMetricValue"] {{
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, {PALETTE['blue']}, {PALETTE['purple']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  h1, h2, h3, h4, h5, h6 {{ color: {PALETTE['text']} !important; }}
  p, span, label, div {{ color: {PALETTE['text']}; }}
</style>
"""


def inject_custom_css() -> None:
    """Inject all custom CSS into the Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header() -> None:
    """Render the hero banner at the top of the page."""
    st.markdown(
        f"""
        <div class="hero-card">
            <h1 class="hero-title">🤖 Autonomous Task Agent</h1>
            <p class="hero-subtitle">
                State-Based LangGraph Orchestration · ML Intent Classification (97.25% acc.) ·
                ChromaDB Vector Memory · Human-in-the-Loop Safety Gate
            </p>
            <div class="hero-badges">
                <span class="badge badge-info">LangGraph v2</span>
                <span class="badge badge-purple">Google Gemini</span>
                <span class="badge badge-success">97.25% ML Accuracy</span>
                <span class="badge badge-cyan">ChromaDB Memory</span>
                <span class="badge badge-warning">Human Approval Gate</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_STATUS_STYLE = {
    "COMPLETED":         ("completed",  "badge-success", "✅"),
    "WAITING_APPROVAL":  ("waiting",    "badge-warning", "⏳"),
    "FAILED":            ("failed",     "badge-danger",  "❌"),
    "RETRYING":          ("retrying",   "badge-cyan",    "🔄"),
}


def render_trace_timeline(trace_items: List[Dict[str, Any]]) -> None:
    """Render the execution trace as a vertical timeline."""
    st.markdown(
        '<div class="section-header"><span class="section-icon">⚡</span>Execution Trace</div>',
        unsafe_allow_html=True,
    )

    if not trace_items:
        st.info("No trace events yet — execute a goal to begin.")
        return

    items_html = ""
    for i, item in enumerate(trace_items):
        status_str = item.get("status", "COMPLETED")
        dot_cls, badge_cls, icon = _STATUS_STYLE.get(
            status_str, ("completed", "badge-info", "▶")
        )
        is_last = i == len(trace_items) - 1
        line_html = "" if is_last else '<div class="trace-line"></div>'

        items_html += f"""
        <div class="trace-item">
            <div class="trace-dot-col">
                <div class="trace-dot {dot_cls}"></div>
                {line_html}
            </div>
            <div class="trace-content">
                <div class="trace-meta">
                    <span class="trace-time">{item.get('timestamp', '')}</span>
                    <span class="badge {badge_cls}">{icon} {status_str}</span>
                </div>
                <div class="trace-step-name">{item.get('step_name', '')}</div>
                <div class="trace-details">{item.get('details', '')}</div>
            </div>
        </div>
        """

    st.markdown(
        f'<div class="trace-wrapper">{items_html}</div>',
        unsafe_allow_html=True,
    )


def render_metric_row(metrics: List[Dict[str, Any]]) -> None:
    """
    Render a horizontal row of metric cards.

    Parameters
    ----------
    metrics : list of dicts with keys 'value', 'label', and optionally 'delta'.
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{m['value']}</div>
                    <div class="metric-label">{m['label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_memory_item(m: Dict[str, Any]) -> None:
    """Render a single memory record as a styled card."""
    mem_type = m.get("memory_type", "preference")
    badge_cls = {
        "preference": "badge-purple",
        "note": "badge-info",
        "background": "badge-cyan",
    }.get(mem_type, "badge-info")

    st.markdown(
        f"""
        <div class="memory-item">
            <span class="badge {badge_cls}">{mem_type}</span>
            <div class="memory-content">{m['content']}</div>
            <div class="memory-meta">
                ID: {m.get('memory_id', '—')} &nbsp;·&nbsp; {m.get('created_at', '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
