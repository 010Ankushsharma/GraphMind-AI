"""Centralized prompts for query and answer generation."""
from app.graph.schema import (
    ALLOWED_OPERATIONS,
    ALLOWED_OPERATORS,
    ENTITY_PROPERTIES,
    RELATIONSHIP_SCHEMA,
)

QUERY_GENERATION_SYSTEM = """You are the query-planning component of an e-commerce Knowledge Graph system.

Your only job is to translate the user's natural-language question into a valid GraphQuery JSON object.

You must use only the provided graph schema.

Do not invent entity types.
Do not invent relationships.
Do not invent properties.
Do not generate Python.
Do not generate Cypher.
Do not answer the user's question.
Do not use outside knowledge.

If the question cannot be represented using the available graph schema, return JSON:
{"unsupported": true, "reason": "<short explanation>"}

Only create read operations (match or count).

The generated query must be deterministic and limited to the allowed schema.

Return ONLY valid JSON with no markdown fences."""


def build_query_schema_prompt() -> str:
    lines = [
        "Graph schema:",
        "",
        "Entity types and properties:",
    ]
    for entity, props in sorted(ENTITY_PROPERTIES.items()):
        prop_list = sorted(p for p in props if p != "entity_type")
        lines.append(f"- {entity}: {', '.join(prop_list)}")

    lines.append("")
    lines.append("Relationships (source -> relationship -> target):")
    for source, rels in sorted(RELATIONSHIP_SCHEMA.items()):
        for rel, target in sorted(rels.items()):
            lines.append(f"- {source} --[{rel}]--> {target}")

    lines.append("")
    lines.append(f"Allowed operations: {', '.join(sorted(ALLOWED_OPERATIONS))}")
    lines.append(f"Allowed filter operators: {', '.join(sorted(ALLOWED_OPERATORS))}")
    lines.append("")
    lines.append(
        "GraphQuery JSON shape for supported questions:"
    )
    lines.append(
        '{"operation":"match|count","source_entity":"...","relationships":[],'
        '"filters":[{"property":"...","operator":"...","value":"..."}],'
        '"return_fields":["..."],"limit":50}'
    )
    return "\n".join(lines)


QUERY_REPAIR_USER = """The previous response was not valid JSON or did not match the schema.
Return ONLY corrected JSON matching GraphQuery or unsupported format. No markdown."""


ANSWER_GENERATION_SYSTEM = """You are the answer-generation component of a Knowledge Graph retrieval system.

Answer the user's question using ONLY the supplied retrieved graph data.

Rules:
1. Do not use outside knowledge.
2. Do not guess.
3. Do not infer unsupported facts.
4. Do not invent values.
5. Do not add information that is not present in the retrieved records.
6. If the retrieved data is empty or insufficient, clearly state that the information is not available in the Knowledge Graph.
7. Keep the answer concise and directly relevant."""
