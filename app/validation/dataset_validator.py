"""Validate relational consistency of loaded dataset."""
from dataclasses import dataclass

from app.graph.models import DatasetBundle


@dataclass
class DatasetValidationResult:
    valid: bool
    errors: list[str]


def validate_dataset(bundle: DatasetBundle) -> DatasetValidationResult:
    errors: list[str] = []

    brand_ids = {r["brand_id"] for r in bundle.brands}
    category_ids = {r["category_id"] for r in bundle.categories}
    vendor_ids = {r["vendor_id"] for r in bundle.vendors}
    customer_ids = {r["customer_id"] for r in bundle.customers}
    product_ids = {r["product_id"] for r in bundle.products}
    order_ids = {r["order_id"] for r in bundle.orders}

    def _dup_check(rows: list[dict], key: str, label: str) -> None:
        seen: set[str] = set()
        for row in rows:
            val = row[key]
            if val in seen:
                errors.append(f"Duplicate {label} id: {val}")
            seen.add(val)

    _dup_check(bundle.brands, "brand_id", "brand")
    _dup_check(bundle.categories, "category_id", "category")
    _dup_check(bundle.vendors, "vendor_id", "vendor")
    _dup_check(bundle.customers, "customer_id", "customer")
    _dup_check(bundle.products, "product_id", "product")
    _dup_check(bundle.orders, "order_id", "order")
    _dup_check(bundle.order_items, "order_item_id", "order_item")

    for p in bundle.products:
        if p["brand_id"] not in brand_ids:
            errors.append(f"Product {p['product_id']} invalid brand_id")
        if p["category_id"] not in category_ids:
            errors.append(f"Product {p['product_id']} invalid category_id")
        if p["vendor_id"] not in vendor_ids:
            errors.append(f"Product {p['product_id']} invalid vendor_id")

    for o in bundle.orders:
        if o["customer_id"] not in customer_ids:
            errors.append(f"Order {o['order_id']} invalid customer_id")

    for item in bundle.order_items:
        if item["order_id"] not in order_ids:
            errors.append(f"Order item {item['order_item_id']} invalid order_id")
        if item["product_id"] not in product_ids:
            errors.append(f"Order item {item['order_item_id']} invalid product_id")

    return DatasetValidationResult(valid=len(errors) == 0, errors=errors)
