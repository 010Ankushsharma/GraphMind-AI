"""Application bootstrap: load graph and wire dependencies."""
import logging
from functools import lru_cache

import networkx as nx

from app.config.settings import Settings, get_settings
from app.graph.builder import build_graph_from_data_dir
from app.graph.loader import load_dataset
from app.llm.factory import LLMProviderFactory
from app.llm.base import BaseLLMProvider
from app.retrieval.service import QueryPipelineService
from app.validation.banana_validator import validate_banana_requirement
from app.validation.dataset_validator import validate_dataset
from app.validation.graph_validator import validate_graph

logger = logging.getLogger(__name__)


@lru_cache
def get_graph() -> nx.MultiDiGraph:
    settings = get_settings()
    data_dir = settings.data_path
    bundle = load_dataset(data_dir)
    ds_result = validate_dataset(bundle)
    if not ds_result.valid:
        raise RuntimeError(f"Dataset validation failed: {ds_result.errors}")

    graph = build_graph_from_data_dir(data_dir)
    g_result = validate_graph(graph)
    if not g_result.valid:
        raise RuntimeError(f"Graph validation failed: {g_result.errors}")

    banana = validate_banana_requirement(graph)
    if not banana.passed:
        raise RuntimeError(
            f"Banana validation failed: expected {banana.expected_count}, "
            f"got {banana.actual_count}"
        )
    logger.info("Banana validation passed")
    return graph


@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    return LLMProviderFactory.create(get_settings())


def get_pipeline() -> QueryPipelineService:
    return QueryPipelineService(
        graph=get_graph(),
        llm_provider=get_llm_provider(),
        settings=get_settings(),
    )


def configure_logging(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(levelname)s  %(message)s",
    )
