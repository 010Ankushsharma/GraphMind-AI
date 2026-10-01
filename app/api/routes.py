from fastapi import APIRouter, HTTPException

from app.api.schemas import QueryRequest, QueryResponse
from app.bootstrap import get_graph, get_llm_provider, get_pipeline
from app.graph.stats import graph_statistics
from app.llm.factory import ResolvingLLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.validation.banana_validator import validate_banana_requirement

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health():
    settings_provider = get_llm_provider()
    provider_name = settings_provider.name
    llm_ok = True
    if isinstance(settings_provider, OllamaProvider):
        llm_ok = settings_provider.health_check()
    elif isinstance(settings_provider, ResolvingLLMProvider):
        llm_ok = True

    try:
        get_graph()
        graph_loaded = True
    except Exception:
        graph_loaded = False

    return {
        "status": "ok" if graph_loaded else "degraded",
        "graph_loaded": graph_loaded,
        "llm_provider": provider_name,
        "llm_reachable": llm_ok,
    }


@router.get("/graph/stats")
def graph_stats():
    graph = get_graph()
    return graph_statistics(graph)


@router.get("/banana-check")
def banana_check():
    result = validate_banana_requirement(get_graph())
    return {
        "expected": result.expected_count,
        "actual": result.actual_count,
        "status": result.status,
        "matching_nodes": result.matching_nodes,
    }


@router.post("/query", response_model=QueryResponse)
def query(body: QueryRequest):
    try:
        result = get_pipeline().answer_question(body.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return QueryResponse(**result)
