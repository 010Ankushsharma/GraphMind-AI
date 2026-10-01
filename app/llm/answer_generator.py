"""Generate grounded natural-language answers from retrieved graph evidence."""
import json
import logging

from app.llm.base import BaseLLMProvider
from app.llm.prompts import ANSWER_GENERATION_SYSTEM

logger = logging.getLogger(__name__)

NOT_AVAILABLE = (
    "The requested information is not available in the Knowledge Graph."
)


class AnswerGenerator:
    def __init__(self, provider: BaseLLMProvider):
        self._provider = provider

    def generate(self, question: str, retrieved_data: dict) -> str:
        grounded = self._apply_grounding_rules(question, retrieved_data)
        if grounded is not None:
            return grounded

        payload = json.dumps(retrieved_data, indent=2, default=str)
        user_prompt = (
            f"User question: {question}\n\n"
            f"Retrieved graph data:\n{payload}\n\n"
            "Answer using only the retrieved graph data."
        )
        response = self._provider.generate_text(
            ANSWER_GENERATION_SYSTEM,
            user_prompt,
        )
        logger.info("Answer generated")
        return response.text.strip()

    def _apply_grounding_rules(
        self, question: str, retrieved_data: dict
    ) -> str | None:
        count = retrieved_data.get("count", 0)
        records = retrieved_data.get("records") or []
        q = question.lower()

        if "headquarters" in q or "address" in q:
            has_address_field = any(
                any(k in (r or {}) for k in ("headquarters", "address", "hq_address"))
                for r in records
            )
            if not has_address_field:
                return NOT_AVAILABLE

        if count == 0 and not records:
            if any(
                kw in q
                for kw in (
                    "how many",
                    "which",
                    "what",
                    "who",
                    "list",
                    "show",
                )
            ):
                return NOT_AVAILABLE
        return None
