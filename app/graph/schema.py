"""Knowledge graph schema definitions for query validation and LLM prompts."""

ENTITY_TYPES = frozenset(
    {"Product", "Brand", "Category", "Vendor", "Order", "Customer"}
)

RELATIONSHIPS = frozenset(
    {"MADE_BY", "BELONGS_TO", "SUPPLIED_BY", "PLACED", "CONTAINS"}
)

# Directed: source_entity -> (relationship, target_entity)
RELATIONSHIP_SCHEMA: dict[str, dict[str, str]] = {
    "Product": {
        "MADE_BY": "Brand",
        "BELONGS_TO": "Category",
        "SUPPLIED_BY": "Vendor",
    },
    "Customer": {
        "PLACED": "Order",
    },
    "Order": {
        "CONTAINS": "Product",
    },
}

# Reverse lookup for traversals starting from target side (optional paths)
INVERSE_RELATIONSHIPS: dict[tuple[str, str], tuple[str, str]] = {
    ("Brand", "MADE_BY"): ("Product", "MADE_BY"),
    ("Category", "BELONGS_TO"): ("Product", "BELONGS_TO"),
    ("Vendor", "SUPPLIED_BY"): ("Product", "SUPPLIED_BY"),
    ("Order", "PLACED"): ("Customer", "PLACED"),
    ("Product", "CONTAINS"): ("Order", "CONTAINS"),
}

ENTITY_PROPERTIES: dict[str, frozenset[str]] = {
    "Product": frozenset(
        {"product_id", "name", "price", "description", "entity_type"}
    ),
    "Brand": frozenset({"brand_id", "name", "entity_type"}),
    "Category": frozenset({"category_id", "name", "entity_type"}),
    "Vendor": frozenset({"vendor_id", "name", "entity_type"}),
    "Customer": frozenset({"customer_id", "name", "email", "entity_type"}),
    "Order": frozenset(
        {"order_id", "order_date", "status", "entity_type"}
    ),
}

ALLOWED_OPERATIONS = frozenset({"match", "count"})
ALLOWED_OPERATORS = frozenset(
    {"equals", "case_insensitive_equals", "contains", "starts_with"}
)
