from app.bootstrap import get_pipeline


def test_pipeline_nike_vendor_a():
    pipeline = get_pipeline()
    result = pipeline.answer_question(
        "Which products from Nike are supplied by Vendor A?"
    )
    ids = {r["product_id"] for r in result["retrieved_data"]["records"]}
    assert {"P001", "P002", "P019"}.issubset(ids)


def test_pipeline_rahul_orders_count():
    pipeline = get_pipeline()
    result = pipeline.answer_question("How many orders has Rahul placed?")
    assert result["retrieved_data"]["count"] == 3
