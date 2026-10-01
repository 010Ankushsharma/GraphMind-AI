import pytest

from app.retrieval.query_models import GraphFilter, GraphQuery, GraphRelationshipTraversal
from app.retrieval.query_validator import QueryValidationError, validate_query_plan


def test_valid_match_query():
    plan = GraphQuery(
        operation="match",
        source_entity="Product",
        return_fields=["product_id", "name"],
    )
    result = validate_query_plan(plan, max_hops=4, max_results=50)
    assert result.query.operation == "match"


def test_unknown_entity_rejected():
    plan = GraphQuery(
        operation="match",
        source_entity="AlienProduct",
        return_fields=["product_id"],
    )
    with pytest.raises(QueryValidationError):
        validate_query_plan(plan, max_hops=4, max_results=50)


def test_unknown_relationship_rejected():
    plan = GraphQuery(
        operation="match",
        source_entity="Product",
        relationships=[
            GraphRelationshipTraversal(
                relationship="FLIES_TO",
                target_entity="Brand",
            )
        ],
        return_fields=["product_id"],
    )
    with pytest.raises(QueryValidationError):
        validate_query_plan(plan, max_hops=4, max_results=50)


def test_excessive_hops_rejected():
    rel = GraphRelationshipTraversal(
        relationship="MADE_BY", target_entity="Brand"
    )
    plan = GraphQuery(
        operation="match",
        source_entity="Product",
        relationships=[rel, rel, rel, rel, rel],
        return_fields=["product_id"],
        limit=10,
    )
    with pytest.raises(QueryValidationError):
        validate_query_plan(plan, max_hops=4, max_results=50)


def test_invalid_property_rejected():
    plan = GraphQuery(
        operation="match",
        source_entity="Product",
        filters=[
            GraphFilter(property="secret_code", operator="equals", value="x")
        ],
        return_fields=["product_id"],
    )
    with pytest.raises(QueryValidationError):
        validate_query_plan(plan, max_hops=4, max_results=50)
