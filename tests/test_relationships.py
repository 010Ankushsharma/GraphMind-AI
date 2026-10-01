def _has_edge(graph, rel: str) -> bool:
    return any(d.get("relationship") == rel for _, _, d in graph.edges(data=True))


def test_relationship_types_exist(graph):
    for rel in ("MADE_BY", "BELONGS_TO", "SUPPLIED_BY", "PLACED", "CONTAINS"):
        assert _has_edge(graph, rel)


def test_product_to_brand_direction(graph):
    found = False
    for u, v, d in graph.edges(data=True):
        if d.get("relationship") != "MADE_BY":
            continue
        if graph.nodes[u].get("entity_type") == "Product":
            assert graph.nodes[v].get("entity_type") == "Brand"
            found = True
    assert found


def test_customer_order_product_path(graph):
    customers = [
        n
        for n, d in graph.nodes(data=True)
        if d.get("entity_type") == "Customer" and d.get("name") == "Rahul"
    ]
    assert customers
    cust = customers[0]
    order_nodes = [
        v
        for _, v, d in graph.out_edges(cust, data=True)
        if d.get("relationship") == "PLACED"
    ]
    assert order_nodes
    products = set()
    for order in order_nodes:
        for _, prod, d in graph.out_edges(order, data=True):
            if d.get("relationship") == "CONTAINS":
                products.add(prod)
    assert products
