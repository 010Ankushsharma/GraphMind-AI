"""Load e-commerce CSV dataset from disk."""
import csv
import logging
from pathlib import Path

from app.graph.models import DatasetBundle

logger = logging.getLogger(__name__)

REQUIRED_FILES = {
    "products.csv": [
        "product_id",
        "name",
        "price",
        "description",
        "brand_id",
        "category_id",
        "vendor_id",
    ],
    "brands.csv": ["brand_id", "name"],
    "categories.csv": ["category_id", "name"],
    "vendors.csv": ["vendor_id", "name"],
    "customers.csv": ["customer_id", "name", "email"],
    "orders.csv": ["order_id", "customer_id", "order_date", "status"],
    "order_items.csv": [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    ],
}


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def load_dataset(data_dir: Path) -> DatasetBundle:
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    for filename, columns in REQUIRED_FILES.items():
        filepath = data_dir / filename
        if not filepath.is_file():
            raise FileNotFoundError(f"Missing dataset file: {filepath}")
        rows = _read_csv(filepath)
        if not rows:
            raise ValueError(f"Dataset file is empty: {filepath}")
        header = set(rows[0].keys())
        missing = set(columns) - header
        if missing:
            raise ValueError(f"{filename} missing columns: {sorted(missing)}")

    bundle = DatasetBundle(
        products=_read_csv(data_dir / "products.csv"),
        brands=_read_csv(data_dir / "brands.csv"),
        categories=_read_csv(data_dir / "categories.csv"),
        vendors=_read_csv(data_dir / "vendors.csv"),
        customers=_read_csv(data_dir / "customers.csv"),
        orders=_read_csv(data_dir / "orders.csv"),
        order_items=_read_csv(data_dir / "order_items.csv"),
    )
    logger.info("Dataset loaded from %s", data_dir)
    return bundle
