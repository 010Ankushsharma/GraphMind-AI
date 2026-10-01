"""Compute graph statistics from NetworkX graph."""
import networkx as nx

from app.validation.banana_validator import validate_banana_requirement


def count_entities(graph: nx.MultiDiGraph, entity_type: str) -> int:
    return sum(
        1
        for _, data in graph.nodes(data=True)
        if data.get("entity_type") == entity_type
    )


def graph_statistics(graph: nx.MultiDiGraph) -> dict:
    banana = validate_banana_requirement(graph)
    return {
        "products": count_entities(graph, "Product"),
        "brands": count_entities(graph, "Brand"),
        "categories": count_entities(graph, "Category"),
        "vendors": count_entities(graph, "Vendor"),
        "customers": count_entities(graph, "Customer"),
        "orders": count_entities(graph, "Order"),
        "nodes": graph.number_of_nodes(),
        "relationships": graph.number_of_edges(),
        "banana_count": banana.actual_count,
    }
