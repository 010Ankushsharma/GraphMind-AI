"""Pydantic models for the safe graph query DSL."""
from typing import Literal

from pydantic import BaseModel, Field

Operation = Literal["match", "count"]
FilterOperator = Literal[
    "equals", "case_insensitive_equals", "contains", "starts_with"
]


class GraphFilter(BaseModel):
    property: str
    operator: FilterOperator
    value: str | int | float


class GraphRelationshipTraversal(BaseModel):
    relationship: str
    target_entity: str
    target_filter: GraphFilter | None = None


class GraphQuery(BaseModel):
    operation: Operation
    source_entity: str
    relationships: list[GraphRelationshipTraversal] = Field(default_factory=list)
    filters: list[GraphFilter] = Field(default_factory=list)
    return_fields: list[str] = Field(default_factory=list)
    limit: int = Field(default=50, ge=1)


class UnsupportedGraphQuery(BaseModel):
    unsupported: Literal[True] = True
    reason: str
