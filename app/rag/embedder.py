# """
# Embedding generation for schema documentation.
# Uses OpenAI-compatible API to create vector representations of table docs.
# """

# from openai import OpenAI

# from app.core import settings
# from app.rag.schema_docs import TABLE_DOCS

# _EMBEDDING_MODEL = "text-embedding-3-large"
# _VECTOR_SIZE = 3072

# _client = OpenAI(
#     base_url="https://api.gapgpt.app/v1",
#     api_key=settings.OPENAI_API_KEY,
# )


# def _embed(text: str) -> list[float]:
#     return (
#         _client.embeddings.create(
#             model=_EMBEDDING_MODEL,
#             input=text,
#         )
#         .data[0]
#         .embedding
#     )


# def generate_embeddings(
#     docs: list[dict[str, str]] | None = None,
# ) -> list[dict]:

#     source = docs if docs is not None else TABLE_DOCS

#     return [
#         {
#             "table": doc["table"],
#             "chunk_type": doc["chunk_type"],
#             "text": doc["text"],
#             "vector": _embed(doc["text"]),
#         }
#         for doc in source
#     ]


# VECTOR_SIZE = _VECTOR_SIZE



















"""
Embedding generation for schema documentation.
Uses OpenAI-compatible API to create vector representations of table docs.
Supports both dense (text-embedding-3-large) and sparse (BM25) vectors.
"""

from fastembed import SparseTextEmbedding
from openai import OpenAI

from app.core import settings
from app.rag.schema_docs import TABLE_DOCS

_EMBEDDING_MODEL = "text-embedding-3-large"
_VECTOR_SIZE = 3072

_client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=settings.OPENAI_API_KEY,
)

_sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")


def _embed_dense(text: str) -> list[float]:
    return (
        _client.embeddings.create(
            model=_EMBEDDING_MODEL,
            input=text,
        )
        .data[0]
        .embedding
    )


def _embed_sparse(text: str) -> dict:
    result = list(_sparse_model.embed([text]))[0]
    return {
        "indices": result.indices.tolist(),
        "values": result.values.tolist(),
    }


def generate_embeddings(
    docs: list[dict[str, str]] | None = None,
) -> list[dict]:

    source = docs if docs is not None else TABLE_DOCS

    return [
        {
            "table": doc["table"],
            "chunk_type": doc["chunk_type"],
            "text": doc["text"],
            "dense_vector": _embed_dense(doc["text"]),
            "sparse_vector": _embed_sparse(doc["text"]),
        }
        for doc in source
    ]


VECTOR_SIZE = _VECTOR_SIZE