"""Deterministic LLM mock for tests and offline demos."""
import json
import re

from app.llm.base import BaseLLMProvider, LLMResponse


def _normalize(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())


# Query plans keyed by normalized question substrings (first match wins)
_QUERY_RULES: list[tuple[str, dict]] = [
    (
        "products are made by nike",
        {
            "operation": "match",
            "source_entity": "Product",
            "relationships": [
                {
                    "relationship": "MADE_BY",
                    "target_entity": "Brand",
                    "target_filter": {
                        "property": "name",
                        "operator": "case_insensitive_equals",
                        "value": "Nike",
                    },
                }
            ],
            "filters": [],
            "return_fields": ["product_id", "name"],
            "limit": 50,
        },
    ),
    (
        "products from nike are supplied by vendor a",
        {
            "operation": "match",
            "source_entity": "Product",
            "relationships": [
                {
                    "relationship": "MADE_BY",
                    "target_entity": "Brand",
                    "target_filter": {
                        "property": "name",
                        "operator": "case_insensitive_equals",
                        "value": "Nike",
                    },
                },
                {
                    "relationship": "SUPPLIED_BY",
                    "target_entity": "Vendor",
                    "target_filter": {
                        "property": "name",
                        "operator": "case_insensitive_equals",
                        "value": "Vendor A",
                    },
                },
            ],
            "filters": [],
            "return_fields": ["product_id", "name"],
            "limit": 50,
        },
    ),
    (
        "products are supplied by vendor b",
        {
            "operation": "match",
            "source_entity": "Product",
            "relationships": [
                {
                    "relationship": "SUPPLIED_BY",
                    "target_entity": "Vendor",
                    "target_filter": {
                        "property": "name",
                        "operator": "case_insensitive_equals",
                        "value": "Vendor B",
                    },
                }
            ],
            "filters": [],
            "return_fields": ["product_id", "name"],
            "limit": 50,
        },
    ),
    (
        "category does iphone 17 belong",
        {
            "operation": "match",
            "source_entity": "Product",
            "relationships": [
                {
                    "relationship": "BELONGS_TO",
                    "target_entity": "Category",
                    "target_filter": None,
                }
            ],
            "filters": [
                {
                    "property": "name",
                    "operator": "case_insensitive_equals",
                    "value": "iPhone 17",
                }
            ],
            "return_fields": ["category_id", "name"],
            "limit": 50,
        },
    ),
    (
        "products did rahul order",
        {
            "operation": "match",
            "source_entity": "Customer",
            "relationships": [
                {"relationship": "PLACED", "target_entity": "Order"},
                {"relationship": "CONTAINS", "target_entity": "Product"},
            ],
            "filters": [
                {
                    "property": "name",
                    "operator": "case_insensitive_equals",
                    "value": "Rahul",
                }
            ],
            "return_fields": ["product_id", "name"],
            "limit": 50,
        },
    ),
    (
        "how many orders has rahul placed",
        {
            "operation": "count",
            "source_entity": "Customer",
            "relationships": [
                {"relationship": "PLACED", "target_entity": "Order"},
            ],
            "filters": [
                {
                    "property": "name",
                    "operator": "case_insensitive_equals",
                    "value": "Rahul",
                }
            ],
            "return_fields": [],
            "limit": 50,
        },
    ),
    (
        "how many banana products",
        {
            "operation": "count",
            "source_entity": "Product",
            "relationships": [],
            "filters": [
                {
                    "property": "name",
                    "operator": "case_insensitive_equals",
                    "value": "banana",
                }
            ],
            "return_fields": [],
            "limit": 50,
        },
    ),
    (
        "headquarters address of vendor a",
        {
            "operation": "match",
            "source_entity": "Vendor",
            "relationships": [],
            "filters": [
                {
                    "property": "name",
                    "operator": "case_insensitive_equals",
                    "value": "Vendor A",
                }
            ],
            "return_fields": ["vendor_id", "name"],
            "limit": 50,
        },
    ),
]


class MockLLMProvider(BaseLLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        structured_schema: dict | None = None,
    ) -> LLMResponse:
        if "Answer the user's question" in system_prompt:
            return self._answer(user_prompt)

        question = _extract_question(user_prompt)
        nq = _normalize(question)
        for needle, plan in _QUERY_RULES:
            if needle in nq:
                return LLMResponse(text=json.dumps(plan), provider_name=self.name)

        unsupported = {
            "unsupported": True,
            "reason": "Question cannot be mapped to the graph schema in mock mode.",
        }
        return LLMResponse(text=json.dumps(unsupported), provider_name=self.name)

    def _answer(self, user_prompt: str) -> LLMResponse:
        if "Retrieved graph data" in user_prompt:
            block = user_prompt.split("Retrieved graph data:", 1)[-1]
            if '"count": 0' in block or '"records": []' in block:
                if "headquarters" in user_prompt.lower():
                    text = (
                        "The requested information is not available "
                        "in the Knowledge Graph."
                    )
                    return LLMResponse(text=text, provider_name=self.name)
            if "banana" in user_prompt.lower() and '"count": 5' in block:
                return LLMResponse(
                    text="There are 5 banana products in the knowledge graph.",
                    provider_name=self.name,
                )
            if '"count":' in block and "orders has rahul" in user_prompt.lower():
                import re

                m = re.search(r'"count":\s*(\d+)', block)
                if m:
                    return LLMResponse(
                        text=f"Rahul has placed {m.group(1)} orders.",
                        provider_name=self.name,
                    )
        return LLMResponse(
            text="Based on the retrieved graph data, see the records above.",
            provider_name=self.name,
        )


def _extract_question(user_prompt: str) -> str:
    if "User question:" in user_prompt:
        return user_prompt.split("User question:", 1)[-1].strip().split("\n", 1)[0]
    return user_prompt
