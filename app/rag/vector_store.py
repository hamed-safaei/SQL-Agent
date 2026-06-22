# import hashlib

# from qdrant_client import QdrantClient
# from qdrant_client.models import (
#     PointStruct,
#     VectorParams,
#     Distance,
# )

# from app.rag.docs_embeding import generate_embeddings


# client = QdrantClient(url="http://localhost:6333")


# def stable_point_id(table_name: str) -> int:
#     """
#     تولید شناسه ثابت برای هر جدول.
#     باعث می‌شود upsert رکورد قبلی را آپدیت کند
#     و رکورد تکراری ساخته نشود.
#     """
#     return int(
#         hashlib.md5(
#             table_name.encode("utf-8")
#         ).hexdigest()[:12],
#         16,
#     )


# def get_or_create_collection(
#     server_name: str,
#     database_name: str,
#     vector_size: int = 3072,
# ) -> tuple[str, bool]:
#     """
#     Returns:
#         (collection_name, created)
#     """

#     collection_name = (
#         f"{server_name}_{database_name}"
#         .lower()
#         .replace(" ", "_")
#         .replace(".", "_")
#         .replace("-", "_")
#     )

#     collections = client.get_collections().collections
#     collection_names = {c.name for c in collections}

#     if collection_name in collection_names:
#         return collection_name, False

#     client.create_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(
#             size=vector_size,
#             distance=Distance.COSINE,
#         ),
#     )

#     return collection_name, True


# def index_schema_docs(
#     server_name: str,
#     database_name: str,
#     reindex_if_exists: bool = False,
# ) -> dict:
#     """
#     reindex_if_exists:
#         False -> اگر کالکشن وجود داشت کاری نکن
#         True  -> اگر کالکشن وجود داشت دوباره embedding و upsert انجام بده
#     """

#     collection_name, created = get_or_create_collection(
#         server_name=server_name,
#         database_name=database_name,
#     )

#     # کالکشن از قبل وجود دارد و کاربر نمی‌خواهد ری‌ایندکس شود
#     if not created and not reindex_if_exists:
#         return {
#             "collection_name": collection_name,
#             "documents_count": 0,
#             "status": "already_exists",
#             "message": "Collection already exists. Reindex skipped."
#         }

#     vectors = generate_embeddings()

#     points = [
#         PointStruct(
#             id=stable_point_id(v["table"]),
#             vector=v["vector"],
#             payload={
#                 "table": v["table"],
#                 "content": v["text"],
#             },
#         )
#         for v in vectors
#     ]

#     operation_info = client.upsert(
#         collection_name=collection_name,
#         points=points,
#         wait=True,
#     )

#     return {
#         "collection_name": collection_name,
#         "documents_count": len(points),
#         "operation_id": operation_info.operation_id,
#         "status": operation_info.status,
#         "created": created,
#     }





















"""
Vector store operations using Qdrant.
Handles collection lifecycle and document upserts.
"""

import hashlib

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.rag.embedder import VECTOR_SIZE, generate_embeddings

_client = QdrantClient(url="http://localhost:6333")


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


def _stable_id(table_name: str) -> int:
    """Deterministic integer ID for a table name (enables idempotent upserts)."""
    return int(hashlib.md5(table_name.encode()).hexdigest()[:12], 16)


# --------------------------------------------------------------------------- #
#  Public API                                                                  #
# --------------------------------------------------------------------------- #

def collection_exists(server_name: str, database_name: str) -> bool:
    name = _collection_name(server_name, database_name)
    existing = {c.name for c in _client.get_collections().collections}
    return name in existing


def create_collection(server_name: str, database_name: str) -> str:
    """Create a Qdrant collection. Returns the collection name."""
    name = _collection_name(server_name, database_name)
    _client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
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
            "message": "Collection already exists. ",
        }

    if not already_existed:
        create_collection(server_name, database_name)

    vectors = generate_embeddings()
    points = [
        PointStruct(
            id=_stable_id(v["table"]),
            vector=v["vector"],
            payload={"table": v["table"], "content": v["text"]},
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