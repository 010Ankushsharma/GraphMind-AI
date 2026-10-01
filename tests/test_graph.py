def test_required_entity_nodes_exist(graph):
    types = {data["entity_type"] for _, data in graph.nodes(data=True)}
    for et in ("Product", "Brand", "Category", "Vendor", "Order", "Customer"):
        assert et in types


def test_product_nodes_have_properties(graph):
    products = [
        data
        for _, data in graph.nodes(data=True)
        if data.get("entity_type") == "Product"
    ]
    assert products
    sample = products[0]
    assert "product_id" in sample
    assert "name" in sample
    assert "price" in sample
