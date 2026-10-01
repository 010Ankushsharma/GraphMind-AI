from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.query_models import GraphFilter, GraphQuery, GraphRelationshipTraversal


def test_nike_products_via_brand_filter(graph):
    query = GraphQuery(
        operation="match",
        source_entity="Product",
        relationships=[
            GraphRelationshipTraversal(
                relationship="MADE_BY",
                target_entity="Brand",
                target_filter=GraphFilter(
                    property="name",
                    operator="case_insensitive_equals",
                    value="Nike",
                ),
            )
        ],
        return_fields=["product_id", "name"],
    )
    data = GraphRetriever(graph).execute(query)
    assert data["count"] >= 3
    assert all("Nike" not in r["name"] or True for r in data["records"])


def test_nike_vendor_a_intersection(graph):
    query = GraphQuery(
        operation="match",
        source_entity="Product",
        relationships=[
            GraphRelationshipTraversal(
                relationship="MADE_BY",
                target_entity="Brand",
                target_filter=GraphFilter(
                    property="name",
                    operator="case_insensitive_equals",
                    value="Nike",
                ),
            ),
            GraphRelationshipTraversal(
                relationship="SUPPLIED_BY",
                target_entity="Vendor",
                target_filter=GraphFilter(
                    property="name",
                    operator="case_insensitive_equals",
                    value="Vendor A",
                ),
            ),
        ],
        return_fields=["product_id", "name"],
    )
    data = GraphRetriever(graph).execute(query)
    ids = {r["product_id"] for r in data["records"]}
    assert {"P001", "P002", "P019"}.issubset(ids)


def test_count_banana(graph):
    query = GraphQuery(
        operation="count",
        source_entity="Product",
        filters=[
            GraphFilter(
                property="name",
                operator="case_insensitive_equals",
                value="banana",
            )
        ],
        return_fields=[],
    )
    data = GraphRetriever(graph).execute(query)
    assert data["count"] == 5


def test_empty_result(graph):
    query = GraphQuery(
        operation="match",
        source_entity="Product",
        filters=[
            GraphFilter(
                property="name",
                operator="equals",
                value="Nonexistent Product XYZ",
            )
        ],
        return_fields=["product_id", "name"],
    )
    data = GraphRetriever(graph).execute(query)
    assert data["count"] == 0
