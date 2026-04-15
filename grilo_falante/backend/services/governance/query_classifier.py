"""
Query Classifier — Classifies user queries by epistemic type

Enables differentiated handling based on query intent:
- factual_lookup: Direct factual questions
- open_exploration: Exploratory/discussional queries
- corpus_bound: Queries requiring specific document evidence
"""


class QueryType(str):
    FACTUAL_LOOKUP = "factual_lookup"
    OPEN_EXPLORATION = "open_exploration"
    CORPUS_BOUND = "corpus_bound"


FACTUAL_MARKERS = [
    "capital", "who is", "when did", "where is", "what is",
    "qual é", "quem é", "quando é que", "onde fica", "o que é",
    "how many", "how much", "what year", "what date",
]

EXPLORATORY_MARKERS = [
    "interesting facts", "tell me about", "overview", "summarize",
    "factos interessantes", "fala-me de", "resumo", "explica", "quais são",
    "can you explain", "what do you think", "your opinion",
]

CORPUS_MARKERS = [
    "according to the document", "in the paper", "according to your data",
    "de acordo com o documento", "no artigo", "nos dados locais", "na base local",
    "in your knowledge base", "from your training",
]


def classify_query(query: str) -> str:
    """
    Classify a user query by epistemic type.

    Args:
        query: The user's query text

    Returns:
        QueryType enum value as string
    """
    q = query.lower().strip()

    if any(x in q for x in CORPUS_MARKERS):
        return QueryType.CORPUS_BOUND

    if any(x in q for x in EXPLORATORY_MARKERS):
        return QueryType.OPEN_EXPLORATION

    if any(x in q for x in FACTUAL_MARKERS):
        return QueryType.FACTUAL_LOOKUP

    return QueryType.OPEN_EXPLORATION


def requires_evidence(query_type: str) -> bool:
    """Check if a query type requires strong evidence backing."""
    return query_type in (QueryType.FACTUAL_LOOKUP, QueryType.CORPUS_BOUND)


def allows_speculation(query_type: str) -> bool:
    """Check if a query type allows speculative responses."""
    return query_type == QueryType.OPEN_EXPLORATION
