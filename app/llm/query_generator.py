"""Translate natural language to validated GraphQuery plans."""
import json
import logging
import re

from pydantic import ValidationError

from app.llm.base import BaseLLMProvider
from app.llm.prompts import (
    QUERY_GENERATION_SYSTEM,
    QUERY_REPAIR_USER,
    build_query_schema_prompt,
)
from app.retrieval.query_models import GraphQuery, UnsupportedGraphQuery

logger = logging.getLogger(__name__)


class QueryGenerationError(Exception):
    """Failed to produce a valid query plan after retries."""


def _strip_json(text: str) -> str:
    cleaned = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    return cleaned


def _parse_plan(raw: str) -> GraphQuery | UnsupportedGraphQuery:
    data = json.loads(_strip_json(raw))
    if data.get("unsupported") is True:
        return UnsupportedGraphQuery.model_validate(data)
    return GraphQuery.model_validate(data)


class QueryGenerator:
    def __init__(self, provider: BaseLLMProvider):
        self._provider = provider

    def generate(self, question: str) -> GraphQuery | UnsupportedGraphQuery:
        schema = build_query_schema_prompt()
        user_prompt = f"{schema}\n\nUser question: {question}"
        raw = self._provider.generate_text(
            QUERY_GENERATION_SYSTEM,
            user_prompt,
            structured_schema={"type": "object"},
        ).text
        try:
            plan = _parse_plan(raw)
            logger.info("Query plan generated")
            return plan
        except (json.JSONDecodeError, ValidationError) as first_err:
            logger.warning("Malformed query plan, attempting repair: %s", first_err)
            repair_prompt = (
                f"{user_prompt}\n\nPrevious invalid output:\n{raw}\n\n{QUERY_REPAIR_USER}"
            )
            raw2 = self._provider.generate_text(
                QUERY_GENERATION_SYSTEM,
                repair_prompt,
                structured_schema={"type": "object"},
            ).text
            try:
                plan = _parse_plan(raw2)
                logger.info("Query plan repaired successfully")
                return plan
            except (json.JSONDecodeError, ValidationError) as second_err:
                raise QueryGenerationError(
                    f"Could not parse query plan: {second_err}"
                ) from second_err
