"""Validate required entities and relationships exist in the graph."""
from dataclasses import dataclass

import networkx as nx

from app.graph.builder import (
    REL_BELONGS_TO,
    REL_CONTAINS,
    REL_MADE_BY,
    REL_PLACED,
    REL_SUPPLIED_BY,
)

REQUIRED_ENTITIES = (
    "Product",
    "Brand",
    "Category",
    "Vendor",
    "Order",
    "Customer",
)

REQUIRED_EDGE_TYPES = (
    REL_MADE_BY,
    REL_BELONGS_TO,
    REL_SUPPLIED_BY,
    REL_PLACED,
    REL_CONTAINS,
)


@dataclass
class GraphValidationResult:
    valid: bool
    errors: list[str]


def validate_graph(graph: nx.MultiDiGraph) -> GraphValidationResult:
    errors: list[str] = []
    present_types = {
        data.get("entity_type")
        for _, data in graph.nodes(data=True)
        if data.get("entity_type")
    }
    for et in REQUIRED_ENTITIES:
        if et not in present_types:
            errors.append(f"Missing entity type: {et}")

    edge_rels = {
        data.get("relationship")
        for _, _, data in graph.edges(data=True)
        if data.get("relationship")
    }
    for rel in REQUIRED_EDGE_TYPES:
        if rel not in edge_rels:
            errors.append(f"Missing relationship type: {rel}")

    return GraphValidationResult(valid=len(errors) == 0, errors=errors)
