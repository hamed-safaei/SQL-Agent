# from app.rag import (
#     order_items_text,
#     brands_text,
#     orders_text,
#     staffs_text,
#     stocks_text,
#     stores_text,
#     products_text,
#     customers_text,
#     categories_text,
# )

# from openai import OpenAI
# from app.core import settings


# BASE_URL = "https://api.gapgpt.app/v1"
# API_KEY = settings.OPENAI_API_KEY


# client_openai = OpenAI(
#     base_url=BASE_URL,
#     api_key=API_KEY,
# )


# def generate_embeddings():
#     docs = [
#         {"table": "sales.customers", "text": customers_text},
#         {"table": "sales.orders", "text": orders_text},
#         {"table": "sales.order_items", "text": order_items_text},
#         {"table": "production.products", "text": products_text},
#         {"table": "production.brands", "text": brands_text},
#         {"table": "production.categories", "text": categories_text},
#         {"table": "production.stocks", "text": stocks_text},
#         {"table": "sales.stores", "text": stores_text},
#         {"table": "sales.staffs", "text": staffs_text},
#     ]

#     vectors = []

#     for doc in docs:
#         embedding = client_openai.embeddings.create(
#             model="text-embedding-3-large",
#             input=doc["text"]
#         ).data[0].embedding

#         vectors.append({
#             "table": doc["table"],
#             "text": doc["text"],
#             "vector": embedding,
#         })

#     return vectors

























"""
Embedding generation for schema documentation.
Uses OpenAI-compatible API to create vector representations of table docs.
"""

from openai import OpenAI

from app.core import settings
from app.rag.schema_docs import TABLE_DOCS

_EMBEDDING_MODEL = "text-embedding-3-large"
_VECTOR_SIZE = 3072

_client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=settings.OPENAI_API_KEY,
)


def _embed(text: str) -> list[float]:
    """Single embedding call — isolated for easy mocking in tests."""
    return (
        _client.embeddings.create(
            model=_EMBEDDING_MODEL,
            input=text,
        )
        .data[0]
        .embedding
    )


def generate_embeddings(
    docs: list[dict[str, str]] | None = None,
) -> list[dict]:
    """
    Generate embeddings for a list of table documents.

    Args:
        docs: List of {"table": ..., "text": ...} dicts.
              Defaults to TABLE_DOCS from schema_docs.py.

    Returns:
        List of {"table": ..., "text": ..., "vector": [...]} dicts.
    """
    source = docs if docs is not None else TABLE_DOCS

    return [
        {
            "table": doc["table"],
            "text":  doc["text"],
            "vector": _embed(doc["text"]),
        }
        for doc in source
    ]


VECTOR_SIZE = _VECTOR_SIZE