"""Generate docs/sample_queries.md from mock pipeline execution."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LLM_PROVIDER", "mock")

from app.bootstrap import (  # noqa: E402
    configure_logging,
    get_graph,
    get_llm_provider,
    get_pipeline,
)
from app.config.settings import get_settings  # noqa: E402

QUESTIONS = [
    "Which products are made by Nike?",
    "Which products from Nike are supplied by Vendor A?",
    "Which products are supplied by Vendor B?",
    "Which category does iPhone 17 belong to?",
    "Which products did Rahul order?",
    "How many orders has Rahul placed?",
    "How many banana products are present in the knowledge graph?",
    "What is the headquarters address of Vendor A?",
]


def main() -> None:
    get_settings.cache_clear()
    get_graph.cache_clear()
    get_llm_provider.cache_clear()
    configure_logging(get_settings())
    pipeline = get_pipeline()
    out_path = ROOT / "docs" / "sample_queries.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# Sample Queries (Generated)\n"]
    for q in QUESTIONS:
        result = pipeline.answer_question(q)
        lines.append(f"## {q}\n")
        lines.append("### Generated Query Plan\n")
        lines.append("```json\n")
        lines.append(json.dumps(result["query_plan"], indent=2))
        lines.append("\n```\n")
        lines.append("### Validation\n")
        lines.append("Query plan validated against schema before retrieval.\n")
        lines.append("### Retrieved Records\n")
        lines.append("```json\n")
        lines.append(json.dumps(result["retrieved_data"], indent=2, default=str))
        lines.append("\n```\n")
        lines.append("### Final Answer\n")
        lines.append(result["answer"] + "\n")
        lines.append("---\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
