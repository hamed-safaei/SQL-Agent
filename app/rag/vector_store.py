# """
# Vector store operations using Qdrant.
# Handles collection lifecycle and document upserts.
# """

# import hashlib

# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, PointStruct, VectorParams

# from app.rag.embedder import VECTOR_SIZE, generate_embeddings

# _client = QdrantClient(url="http://localhost:6333")


# # --------------------------------------------------------------------------- #
# #  Helpers                                                                     #
# # --------------------------------------------------------------------------- #

# def _collection_name(server_name: str, database_name: str) -> str:
#     return (
#         f"{server_name}_{database_name}"
#         .lower()
#         .replace(" ", "_")
#         .replace(".", "_")
#         .replace("-", "_")
#     )


# def _stable_id(table_name: str) -> int:
#     """Deterministic integer ID for a table name (enables idempotent upserts)."""
#     return int(hashlib.md5(table_name.encode()).hexdigest()[:12], 16)


# # --------------------------------------------------------------------------- #
# #  Public API                                                                  #
# # --------------------------------------------------------------------------- #

# def collection_exists(server_name: str, database_name: str) -> bool:
#     name = _collection_name(server_name, database_name)
#     existing = {c.name for c in _client.get_collections().collections}
#     return name in existing


# def create_collection(server_name: str, database_name: str) -> str:
#     """Create a Qdrant collection. Returns the collection name."""
#     name = _collection_name(server_name, database_name)
#     _client.create_collection(
#         collection_name=name,
#         vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
#     )
#     return name


# def index_schema_docs(
#     server_name: str,
#     database_name: str,
#     reindex_if_exists: bool = False,
# ) -> dict:
#     """
#     Embed and upsert table documentation into Qdrant.

#     Args:
#         reindex_if_exists:
#             False → skip if collection already exists (default).
#             True  → re-embed and upsert even if collection exists.

#     Returns:
#         Status dict with collection_name, documents_count, status, etc.
#     """
#     name = _collection_name(server_name, database_name)
#     already_existed = collection_exists(server_name, database_name)

#     if already_existed and not reindex_if_exists:
#         return {
#             "collection_name": name,
#             "documents_count": 0,
#             "status": "skipped",
#             "message": "Collection already exists. ",
#         }

#     if not already_existed:
#         create_collection(server_name, database_name)

#     vectors = generate_embeddings()
#     points = [
#         PointStruct(
#             id=_stable_id(v["table"]),
#             vector=v["vector"],
#             payload={"table": v["table"], "content": v["text"]},
#         )
#         for v in vectors
#     ]

#     result = _client.upsert(collection_name=name, points=points, wait=True)

#     return {
#         "collection_name": name,
#         "documents_count": len(points),
#         "operation_id": result.operation_id,
#         "status": result.status,
#         "created": not already_existed,
#     }










"""
Vector store operations using Qdrant.
Handles collection lifecycle and document upserts.
Supports hybrid search (dense + sparse BM25 with RRF fusion).
"""

import hashlib

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Fusion,
    FusionQuery,
    PointStruct,
    Prefetch,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.rag.embedder import VECTOR_SIZE, generate_embeddings, _embed_dense, _embed_sparse

_client = QdrantClient(url="http://localhost:6333")

_DENSE_VECTOR_NAME = "dense"
_SPARSE_VECTOR_NAME = "sparse"


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _collection_name(server_name: str, database_name: str) -> str:
    return (
        f"{server_name}_{database_name}"
        .lower()
        .replace(" ", "_")
        .replace(".", "_")
        .replace("-", "_")
    )


def _stable_id(table_name: str, chunk_type: str) -> int:
    """Deterministic integer ID based on table + chunk_type (enables idempotent upserts)."""
    key = f"{table_name}::{chunk_type}"
    return int(hashlib.md5(key.encode()).hexdigest()[:12], 16)

# --------------------------------------------------------------------------- #
#  Public API                                                                  #
# --------------------------------------------------------------------------- #

def collection_exists(server_name: str, database_name: str) -> bool:
    name = _collection_name(server_name, database_name)
    existing = {c.name for c in _client.get_collections().collections}
    return name in existing


def create_collection(server_name: str, database_name: str) -> str:
    """Create a Qdrant collection with dense + sparse vectors. Returns the collection name."""
    name = _collection_name(server_name, database_name)
    _client.create_collection(
        collection_name=name,
        vectors_config={
            _DENSE_VECTOR_NAME: VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            )
        },
        sparse_vectors_config={
            _SPARSE_VECTOR_NAME: SparseVectorParams(
                index=SparseIndexParams(on_disk=False)
            )
        },
    )
    return name


def index_schema_docs(
    server_name: str,
    database_name: str,
    reindex_if_exists: bool = False,
) -> dict:
    """
    Embed and upsert table documentation into Qdrant.

    Args:
        reindex_if_exists:
            False → skip if collection already exists (default).
            True  → re-embed and upsert even if collection exists.

    Returns:
        Status dict with collection_name, documents_count, status, etc.
    """
    name = _collection_name(server_name, database_name)
    already_existed = collection_exists(server_name, database_name)

    if already_existed and not reindex_if_exists:
        return {
            "collection_name": name,
            "documents_count": 0,
            "status": "skipped",
            "message": "Collection already exists.",
        }

    if not already_existed:
        create_collection(server_name, database_name)

    vectors = generate_embeddings()


    points = [
        PointStruct(
            id=_stable_id(v["table"], v["chunk_type"]),  # <-- اضافه شد chunk_type
            vector={
                _DENSE_VECTOR_NAME: v["dense_vector"],
                _SPARSE_VECTOR_NAME: SparseVector(
                    indices=v["sparse_vector"]["indices"],
                    values=v["sparse_vector"]["values"],
                ),
            },
            payload={"table": v["table"], "chunk_type": v["chunk_type"], "content": v["text"]},
        )
        for v in vectors
    ]

    result = _client.upsert(collection_name=name, points=points, wait=True)

    return {
        "collection_name": name,
        "documents_count": len(points),
        "operation_id": result.operation_id,
        "status": result.status,
        "created": not already_existed,
    }


def hybrid_search(
    server_name: str,
    database_name: str,
    query: str,
    limit: int = 15,
) -> list[dict]:
    """
    Hybrid search with RRF fusion over dense + sparse vectors.

    Returns:
        List of payloads sorted by fused relevance score.
    """
    name = _collection_name(server_name, database_name)

    dense_query = _embed_dense(query)
    sparse_query = _embed_sparse(query)

    results = _client.query_points(
        collection_name=name,
        prefetch=[
            Prefetch(
                query=dense_query,
                using=_DENSE_VECTOR_NAME,
                limit=20,
            ),
            Prefetch(
                query=SparseVector(
                    indices=sparse_query["indices"],
                    values=sparse_query["values"],
                ),
                using=_SPARSE_VECTOR_NAME,
                limit=20,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=limit,
    )

    return [
        {
            "table": p.payload["table"],
            "chunk": p.payload["chunk_type"],
            "score": round(p.score, 4),
        }
        for p in results.points
    ]