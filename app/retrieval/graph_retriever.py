"""Execute validated GraphQuery plans against NetworkX."""
from typing import Any

import networkx as nx

from app.graph.schema import RELATIONSHIP_SCHEMA
from app.retrieval.query_models import GraphFilter, GraphQuery


class GraphRetriever:
    def __init__(self, graph: nx.MultiDiGraph):
        self._graph = graph

    def _nodes_of_type(self, entity_type: str) -> set[str]:
        return {
            nid
            for nid, data in self._graph.nodes(data=True)
            if data.get("entity_type") == entity_type
        }

    def execute(self, query: GraphQuery) -> dict[str, Any]:
        nodes = self._nodes_of_type(query.source_entity)
        nodes = _apply_filters(nodes, self._graph, query.filters)

        current_entity = query.source_entity
        for hop in query.relationships:
            next_nodes: set[str] = set()
            rel_map = RELATIONSHIP_SCHEMA[current_entity]
            if hop.relationship not in rel_map:
                break
            for nid in nodes:
                for _, target, edge_data in self._graph.out_edges(nid, data=True):
                    if edge_data.get("relationship") != hop.relationship:
                        continue
                    tdata = self._graph.nodes[target]
                    if tdata.get("entity_type") != hop.target_entity:
                        continue
                    if hop.target_filter and not _node_matches_filter(
                        tdata, hop.target_filter
                    ):
                        continue
                    next_nodes.add(target)
            nodes = next_nodes
            current_entity = hop.target_entity

        if query.operation == "count":
            return {"records": [], "count": len(nodes)}

        records: list[dict[str, Any]] = []
        for nid in sorted(nodes):
            data = self._graph.nodes[nid]
            record = {f: data.get(f) for f in query.return_fields}
            records.append(record)
            if len(records) >= query.limit:
                break

        return {"records": records, "count": len(records)}


def _apply_filters(
    node_ids: set[str], graph: nx.MultiDiGraph, filters: list[GraphFilter]
) -> set[str]:
    result = set(node_ids)
    for flt in filters:
        result = {
            nid
            for nid in result
            if _node_matches_filter(graph.nodes[nid], flt)
        }
    return result


def _node_matches_filter(data: dict, flt: GraphFilter) -> bool:
    raw = data.get(flt.property)
    if raw is None:
        return False
    left = str(raw)
    right = str(flt.value)
    op = flt.operator
    if op == "equals":
        return left == right
    if op == "case_insensitive_equals":
        return left.lower() == right.lower()
    if op == "contains":
        return right.lower() in left.lower()
    if op == "starts_with":
        return left.lower().startswith(right.lower())
    return False
