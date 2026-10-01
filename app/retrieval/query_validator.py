"""Validate graph query plans against schema and safety limits."""
from dataclasses import dataclass

from app.graph.schema import (
    ALLOWED_OPERATIONS,
    ALLOWED_OPERATORS,
    ENTITY_PROPERTIES,
    ENTITY_TYPES,
    RELATIONSHIP_SCHEMA,
    RELATIONSHIPS,
)
from app.retrieval.query_models import GraphQuery, UnsupportedGraphQuery


class QueryValidationError(Exception):
    """Raised when a query plan fails validation."""


@dataclass
class ValidatedQuery:
    query: GraphQuery


def validate_query_plan(
    plan: GraphQuery | UnsupportedGraphQuery,
    *,
    max_hops: int,
    max_results: int,
) -> ValidatedQuery | UnsupportedGraphQuery:
    if isinstance(plan, UnsupportedGraphQuery):
        return plan

    q = plan
    if q.operation not in ALLOWED_OPERATIONS:
        raise QueryValidationError(f"Unknown operation: {q.operation}")

    if q.source_entity not in ENTITY_TYPES:
        raise QueryValidationError(f"Unknown entity: {q.source_entity}")

    if len(q.relationships) > max_hops:
        raise QueryValidationError(
            f"Too many relationship hops (max {max_hops})"
        )

    if q.limit > max_results:
        raise QueryValidationError(f"Limit exceeds maximum ({max_results})")

    allowed_return = ENTITY_PROPERTIES.get(q.source_entity, frozenset())
    terminal_entity = q.source_entity
    current_entity = q.source_entity

    for flt in q.filters:
        _validate_filter(current_entity, flt)

    for hop in q.relationships:
        if hop.relationship not in RELATIONSHIPS:
            raise QueryValidationError(f"Unknown relationship: {hop.relationship}")
        rel_map = RELATIONSHIP_SCHEMA.get(current_entity, {})
        expected_target = rel_map.get(hop.relationship)
        if expected_target is None:
            raise QueryValidationError(
                f"Relationship {hop.relationship} invalid from {current_entity}"
            )
        if hop.target_entity != expected_target:
            raise QueryValidationError(
                f"Relationship {hop.relationship} from {current_entity} "
                f"must target {expected_target}, got {hop.target_entity}"
            )
        if hop.target_filter:
            _validate_filter(hop.target_entity, hop.target_filter)
        current_entity = hop.target_entity
        terminal_entity = hop.target_entity

    allowed_return = ENTITY_PROPERTIES.get(terminal_entity, frozenset())
    for field in q.return_fields:
        if field not in allowed_return:
            raise QueryValidationError(
                f"Invalid return field '{field}' for entity {terminal_entity}"
            )

    if q.operation == "match" and not q.return_fields:
        raise QueryValidationError("match operation requires return_fields")

    return ValidatedQuery(query=q)


def _validate_filter(entity: str, flt) -> None:
    if flt.operator not in ALLOWED_OPERATORS:
        raise QueryValidationError(f"Unknown operator: {flt.operator}")
    props = ENTITY_PROPERTIES.get(entity, frozenset())
    if flt.property not in props:
        raise QueryValidationError(
            f"Unknown property '{flt.property}' on entity {entity}"
        )
