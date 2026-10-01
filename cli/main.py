"""Interactive CLI for Knowledge Graph Q&A."""
import json
import os
import sys

# Ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.bootstrap import configure_logging, get_pipeline, get_settings  # noqa: E402


def main() -> None:
    configure_logging(get_settings())
    pipeline = get_pipeline()
    print("E-Commerce Knowledge Graph AI")
    print("--------------------------------")
    print("Type a question (or 'exit'):")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        result = pipeline.answer_question(question)
        print(f"\nProvider: {result['provider']}")
        print("\nQuery Plan:")
        print(json.dumps(result["query_plan"], indent=2))
        print("\nRetrieved Data:")
        print(json.dumps(result["retrieved_data"], indent=2, default=str))
        print("\nFinal Answer:")
        print(result["answer"])
        print("--------------------------------")


if __name__ == "__main__":
    main()
