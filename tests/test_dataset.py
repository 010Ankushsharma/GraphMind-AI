from app.config.settings import get_settings
from app.graph.loader import load_dataset
from app.validation.dataset_validator import validate_dataset


def test_dataset_files_load():
    bundle = load_dataset(get_settings().data_path)
    assert len(bundle.products) >= 25
    assert len(bundle.brands) >= 6
    assert len(bundle.customers) >= 15
    assert len(bundle.orders) >= 30
    assert len(bundle.order_items) >= 50


def test_dataset_referential_integrity():
    bundle = load_dataset(get_settings().data_path)
    result = validate_dataset(bundle)
    assert result.valid, result.errors
