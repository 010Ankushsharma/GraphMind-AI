"""Submission validation script."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config.settings import Settings  # noqa: E402
from app.graph.builder import build_graph_from_data_dir  # noqa: E402
from app.graph.loader import load_dataset  # noqa: E402
from app.retrieval.graph_retriever import GraphRetriever  # noqa: E402
from app.retrieval.query_models import GraphFilter, GraphQuery  # noqa: E402
from app.retrieval.query_validator import validate_query_plan  # noqa: E402
from app.validation.banana_validator import validate_banana_requirement  # noqa: E402
from app.validation.dataset_validator import validate_dataset  # noqa: E402
from app.validation.graph_validator import validate_graph  # noqa: E402


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def main() -> int:
    settings = Settings(LLM_PROVIDER="mock", DATA_DIR="data")
    data_dir = ROOT / settings.data_dir
    results: list[tuple[str, bool]] = []

    print("=========================================")
    print("KNOWLEDGE GRAPH SUBMISSION VALIDATION")
    print("=========================================")
    print()

    try:
        bundle = load_dataset(data_dir)
        ds_ok = validate_dataset(bundle).valid
    except Exception:
        ds_ok = False
    results.append(("Dataset", ds_ok))
    print(f"Dataset ...................... {_status(ds_ok)}")

    try:
        graph = build_graph_from_data_dir(data_dir)
        graph_ok = True
    except Exception:
        graph = None
        graph_ok = False
    results.append(("Graph construction", graph_ok))
    print(f"Graph construction ........... {_status(graph_ok)}")

    entities_ok = False
    rel_ok = False
    banana_ok = False
    banana_retrieval_ok = False
    query_val_ok = False
    sample_ok = False

    if graph is not None:
        entities_ok = validate_graph(graph).valid
        rel_ok = entities_ok
        banana = validate_banana_requirement(graph)
        banana_ok = banana.passed

        q = GraphQuery(
            operation="count",
            source_entity="Product",
            filters=[
                GraphFilter(
                    property="name",
                    operator="case_insensitive_equals",
                    value="banana",
                )
            ],
            return_fields=[],
        )
        retrieved = GraphRetriever(graph).execute(q)
        banana_retrieval_ok = retrieved["count"] == 5

        sample = GraphQuery(
            operation="match",
            source_entity="Product",
            relationships=[],
            filters=[],
            return_fields=["product_id", "name"],
            limit=5,
        )
        try:
            validate_query_plan(sample, max_hops=4, max_results=50)
            query_val_ok = True
            sample_ok = GraphRetriever(graph).execute(sample)["count"] > 0
        except Exception:
            query_val_ok = False
            sample_ok = False

    results.extend(
        [
            ("Required entities", entities_ok),
            ("Relationships", rel_ok),
            ("Banana count = 5", banana_ok),
            ("Banana retrieval", banana_retrieval_ok),
            ("Query validation", query_val_ok),
            ("Sample retrieval", sample_ok),
        ]
    )
    print(f"Required entities ............ {_status(entities_ok)}")
    print(f"Relationships ................ {_status(rel_ok)}")
    print(f"Banana count = 5 ............. {_status(banana_ok)}")
    print(f"Banana retrieval ............. {_status(banana_retrieval_ok)}")
    print(f"Query validation ............. {_status(query_val_ok)}")
    print(f"Sample retrieval ............. {_status(sample_ok)}")
    print()

    overall = all(ok for _, ok in results)
    print(f"OVERALL STATUS: {_status(overall)}")
    print("=========================================")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
