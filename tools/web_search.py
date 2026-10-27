import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from tools.base import BaseTool

logger = logging.getLogger(__name__)


class WebSearchInput(BaseModel):
    query: str = Field(description="Natural-language search query.")
    num_results: int = Field(default=5, ge=1, le=20, description="Number of results to return (1–20).")


class WebSearchTool(BaseTool):
    """
    Searches the web using DuckDuckGo (via duckduckgo-search) with a curated
    mock-result fallback when the network is unavailable or rate-limited.
    """

    name = "web_search"
    description = (
        "Retrieves real-time web search results for any query. "
        "Returns a ranked list of title, snippet, and URL for each result."
    )
    args_schema = WebSearchInput
    requires_approval = False

    # ------------------------------------------------------------------
    # Mock fallback corpus
    # ------------------------------------------------------------------
    _MOCK_TEMPLATES = [
        {
            "title_tpl": "Top Machine Learning Course — {query}",
            "snippet_tpl": (
                "Comprehensive hands-on course covering {query} with Python, "
                "PyTorch, and scikit-learn. Duration: 6 weeks. Price: $49."
            ),
            "url_tpl": "https://example.com/ml-course-1",
        },
        {
            "title_tpl": "Advanced AI & Task Automation Specialisation",
            "snippet_tpl": (
                "Master LLM tool-calling, LangGraph agent workflows, and practical "
                "Python implementations for {query}. Duration: 4 weeks. Price: $79."
            ),
            "url_tpl": "https://example.com/ml-course-2",
        },
        {
            "title_tpl": "Free Introductory Data Science & ML Bootcamp",
            "snippet_tpl": (
                "Beginner-friendly overview for {query} with interactive notebooks. "
                "Duration: 3 weeks. Price: Free."
            ),
            "url_tpl": "https://example.com/ml-course-3",
        },
        {
            "title_tpl": "Python for AI — Practical Guide",
            "snippet_tpl": (
                "Step-by-step guide covering everything from {query} basics to "
                "deploying production ML models. Duration: 8 weeks. Price: $99."
            ),
            "url_tpl": "https://example.com/ml-course-4",
        },
        {
            "title_tpl": "Deep Learning Fundamentals ({query})",
            "snippet_tpl": (
                "Covers neural networks, CNNs, transformers, and real-world {query} "
                "projects. Duration: 10 weeks. Price: $129."
            ),
            "url_tpl": "https://example.com/ml-course-5",
        },
    ]

    def _mock_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        results = []
        for tmpl in self._MOCK_TEMPLATES[:num_results]:
            results.append(
                {
                    "title": tmpl["title_tpl"].format(query=query),
                    "snippet": tmpl["snippet_tpl"].format(query=query),
                    "url": tmpl["url_tpl"],
                    "source": "mock",
                }
            )
        return results

    def _run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        source = "duckduckgo"

        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=num_results))

            for item in raw:
                results.append(
                    {
                        "title": item.get("title", ""),
                        "snippet": item.get("body", ""),
                        "url": item.get("href", ""),
                        "source": "duckduckgo",
                    }
                )
            logger.info(f"[web_search] DuckDuckGo returned {len(results)} results for '{query}'")

        except Exception as exc:
            logger.warning(f"[web_search] DuckDuckGo failed ({exc}); using mock results.")
            results = self._mock_results(query, num_results)
            source = "mock"

        return {
            "query": query,
            "count": len(results),
            "source": source,
            "results": results,
        }
