from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.query_models import GraphFilter, GraphQuery
from app.validation.banana_validator import validate_banana_requirement


def test_banana_count_is_five(graph):
    result = validate_banana_requirement(graph)
    assert result.actual_count == 5
    assert result.status == "PASS"


def test_banana_retrieval_returns_five_records(graph):
    query = GraphQuery(
        operation="match",
        source_entity="Product",
        filters=[
            GraphFilter(
                property="name",
                operator="case_insensitive_equals",
                value="banana",
            )
        ],
        return_fields=["product_id", "name"],
        limit=50,
    )
    data = GraphRetriever(graph).execute(query)
    assert data["count"] == 5
    assert len(data["records"]) == 5
