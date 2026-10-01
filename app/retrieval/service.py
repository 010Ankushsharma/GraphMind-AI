"""End-to-end question answering pipeline."""
import logging
from typing import Any

import networkx as nx

from app.config.settings import Settings
from app.llm.answer_generator import AnswerGenerator
from app.llm.base import BaseLLMProvider
from app.llm.query_generator import QueryGenerator
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.query_models import GraphQuery, UnsupportedGraphQuery
from app.retrieval.query_validator import QueryValidationError, validate_query_plan

logger = logging.getLogger(__name__)


class QueryPipelineService:
    def __init__(
        self,
        graph: nx.MultiDiGraph,
        llm_provider: BaseLLMProvider,
        settings: Settings,
    ):
        self._graph = graph
        self._provider = llm_provider
        self._settings = settings
        self._query_gen = QueryGenerator(llm_provider)
        self._answer_gen = AnswerGenerator(llm_provider)
        self._retriever = GraphRetriever(graph)

    def answer_question(self, question: str) -> dict[str, Any]:
        logger.info("Processing question")
        plan = self._query_gen.generate(question)

        if isinstance(plan, UnsupportedGraphQuery):
            return {
                "question": question,
                "provider": self._provider.name,
                "query_plan": plan.model_dump(),
                "retrieved_data": {"records": [], "count": 0},
                "answer": plan.reason,
                "metadata": {"unsupported": True, "retrieval_count": 0},
            }

        try:
            validated = validate_query_plan(
                plan,
                max_hops=self._settings.max_graph_hops,
                max_results=self._settings.max_query_results,
            )
        except QueryValidationError as exc:
            return {
                "question": question,
                "provider": self._provider.name,
                "query_plan": plan.model_dump(),
                "retrieved_data": {"records": [], "count": 0},
                "answer": f"Invalid query plan: {exc}",
                "metadata": {"validation_error": str(exc), "retrieval_count": 0},
            }

        if isinstance(validated, UnsupportedGraphQuery):
            return {
                "question": question,
                "provider": self._provider.name,
                "query_plan": validated.model_dump(),
                "retrieved_data": {"records": [], "count": 0},
                "answer": validated.reason,
                "metadata": {"unsupported": True, "retrieval_count": 0},
            }

        assert isinstance(validated.query, GraphQuery)
        logger.info("Query plan validated")
        retrieved = self._retriever.execute(validated.query)
        logger.info("Retrieved %s records", retrieved.get("count", 0))

        answer = self._answer_gen.generate(question, retrieved)

        return {
            "question": question,
            "provider": self._provider.name,
            "query_plan": validated.query.model_dump(),
            "retrieved_data": retrieved,
            "answer": answer,
            "metadata": {"retrieval_count": retrieved.get("count", 0)},
        }
