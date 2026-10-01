import pytest
from pydantic import ValidationError

from app.retrieval.query_models import GraphQuery


def test_graph_query_valid():
    q = GraphQuery(
        operation="match",
        source_entity="Product",
        return_fields=["product_id", "name"],
    )
    assert q.operation == "match"


def test_graph_query_invalid_operation():
    with pytest.raises(ValidationError):
        GraphQuery(operation="delete", source_entity="Product")  # type: ignore[arg-type]
