import os

import pytest

os.environ.setdefault("LLM_PROVIDER", "mock")

from app.bootstrap import get_graph, get_llm_provider  # noqa: E402
from app.config.settings import get_settings  # noqa: E402


@pytest.fixture(scope="session")
def graph():
    get_settings.cache_clear()
    get_graph.cache_clear()
    get_llm_provider.cache_clear()
    return get_graph()


@pytest.fixture(scope="session")
def settings():
    return get_settings()
