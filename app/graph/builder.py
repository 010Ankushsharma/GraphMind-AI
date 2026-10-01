"""Build NetworkX MultiDiGraph from dataset."""
import logging
from pathlib import Path

import networkx as nx

from app.graph.loader import load_dataset
from app.graph.models import node_key

logger = logging.getLogger(__name__)

REL_MADE_BY = "MADE_BY"
REL_BELONGS_TO = "BELONGS_TO"
REL_SUPPLIED_BY = "SUPPLIED_BY"
REL_PLACED = "PLACED"
REL_CONTAINS = "CONTAINS"


def build_graph_from_bundle(bundle) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()

    for row in bundle.brands:
        nid = node_key("Brand", row["brand_id"])
        g.add_node(
            nid,
            entity_type="Brand",
            brand_id=row["brand_id"],
            name=row["name"],
        )

    for row in bundle.categories:
        nid = node_key("Category", row["category_id"])
        g.add_node(
            nid,
            entity_type="Category",
            category_id=row["category_id"],
            name=row["name"],
        )

    for row in bundle.vendors:
        nid = node_key("Vendor", row["vendor_id"])
        g.add_node(
            nid,
            entity_type="Vendor",
            vendor_id=row["vendor_id"],
            name=row["name"],
        )

    for row in bundle.customers:
        nid = node_key("Customer", row["customer_id"])
        g.add_node(
            nid,
            entity_type="Customer",
            customer_id=row["customer_id"],
            name=row["name"],
            email=row["email"],
        )

    for row in bundle.orders:
        nid = node_key("Order", row["order_id"])
        g.add_node(
            nid,
            entity_type="Order",
            order_id=row["order_id"],
            order_date=row["order_date"],
            status=row["status"],
        )

    for row in bundle.products:
        nid = node_key("Product", row["product_id"])
        g.add_node(
            nid,
            entity_type="Product",
            product_id=row["product_id"],
            name=row["name"],
            price=float(row["price"]),
            description=row["description"],
        )
        brand_nid = node_key("Brand", row["brand_id"])
        cat_nid = node_key("Category", row["category_id"])
        vendor_nid = node_key("Vendor", row["vendor_id"])
        g.add_edge(nid, brand_nid, relationship=REL_MADE_BY)
        g.add_edge(nid, cat_nid, relationship=REL_BELONGS_TO)
        g.add_edge(nid, vendor_nid, relationship=REL_SUPPLIED_BY)

    for row in bundle.orders:
        cust_nid = node_key("Customer", row["customer_id"])
        order_nid = node_key("Order", row["order_id"])
        g.add_edge(cust_nid, order_nid, relationship=REL_PLACED)

    for row in bundle.order_items:
        order_nid = node_key("Order", row["order_id"])
        prod_nid = node_key("Product", row["product_id"])
        g.add_edge(
            order_nid,
            prod_nid,
            relationship=REL_CONTAINS,
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
        )

    logger.info(
        "Knowledge Graph built: %d nodes, %d edges",
        g.number_of_nodes(),
        g.number_of_edges(),
    )
    return g


def build_graph_from_data_dir(data_dir: Path) -> nx.MultiDiGraph:
    bundle = load_dataset(data_dir)
    return build_graph_from_bundle(bundle)
