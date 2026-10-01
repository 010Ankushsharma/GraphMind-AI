"""Validate exactly five 'banana' product occurrences in the graph."""
from dataclasses import dataclass
from typing import Any

import networkx as nx

EXPECTED_BANANA_COUNT = 5


@dataclass
class BananaValidationResult:
    expected_count: int
    actual_count: int
    status: str
    matching_nodes: list[dict[str, Any]]

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


def _is_banana_product_name(name: str | None) -> bool:
    return name is not None and name.strip().lower() == "banana"


def validate_banana_requirement(graph: nx.MultiDiGraph) -> BananaValidationResult:
    matching: list[dict[str, Any]] = []
    for node_id, data in graph.nodes(data=True):
        if data.get("entity_type") != "Product":
            continue
        if _is_banana_product_name(data.get("name")):
            matching.append(
                {
                    "node_id": node_id,
                    "product_id": data.get("product_id"),
                    "name": data.get("name"),
                }
            )

    actual = len(matching)
    status = "PASS" if actual == EXPECTED_BANANA_COUNT else "FAIL"
    return BananaValidationResult(
        expected_count=EXPECTED_BANANA_COUNT,
        actual_count=actual,
        status=status,
        matching_nodes=matching,
    )
