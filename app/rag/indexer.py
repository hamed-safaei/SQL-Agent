"""
Indexer — orchestrates graph sync and vector indexing together.

This is the single entry-point used by the connection router or any
setup/admin code that needs to bring a new database online.
"""

from app.rag.graph_store import graph_exists, sync_schema_graph
from app.rag.vector_store import collection_exists, index_schema_docs


def setup_rag_for_database(
    server_name: str,
    database_name: str,
    db_url: str,
    force_reindex: bool = False,
) -> dict:
    """
    Full RAG setup for a database connection:
      1. Sync FK relationships → Neo4j  (graph_store)
      2. Embed table docs      → Qdrant  (vector_store)

    Both operations respect force_reindex:
        False → skip if already indexed (no DB calls, no Neo4j calls).
        True  → re-sync and re-embed regardless.

    Returns:
        Combined status dict from both operations.
    """
    graph_result = sync_schema_graph(
        server_name=server_name,
        database_name=database_name,
        db_url=db_url,
        reindex_if_exists=force_reindex,
    )

    vector_result = index_schema_docs(
        server_name=server_name,
        database_name=database_name,
        reindex_if_exists=force_reindex,
    )

    return {
        "graph": graph_result,
        "vector": vector_result,
    }


def is_database_indexed(server_name: str, database_name: str) -> bool:
    """
    Quick check: both graph and vector stores have data for this database.
    Useful for health-checks or deciding whether setup is needed.
    """
    return (
        graph_exists(server_name, database_name)
        and collection_exists(server_name, database_name)
    )