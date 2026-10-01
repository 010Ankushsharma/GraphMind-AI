from app.bootstrap import get_pipeline
from app.config.settings import get_settings
from app.llm.factory import LLMProviderFactory


def test_missing_vendor_address_not_hallucinated():
    get_settings.cache_clear()
    pipeline = get_pipeline()
    result = pipeline.answer_question(
        "What is the headquarters address of Vendor A?"
    )
    answer = result["answer"].lower()
    assert "not available" in answer


def test_banana_count_via_pipeline():
    pipeline = get_pipeline()
    result = pipeline.answer_question(
        "How many banana products are present in the knowledge graph?"
    )
    assert result["retrieved_data"]["count"] == 5
    assert "5" in result["answer"]
