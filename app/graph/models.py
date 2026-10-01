"""Typed views of loaded CSV rows."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetBundle:
    products: list[dict]
    brands: list[dict]
    categories: list[dict]
    vendors: list[dict]
    customers: list[dict]
    orders: list[dict]
    order_items: list[dict]


def node_key(entity_type: str, entity_id: str) -> str:
    return f"{entity_type}:{entity_id}"
