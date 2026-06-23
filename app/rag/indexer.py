from app.rag.graph_store import graph_exists, sync_schema_graph
from app.rag.vector_store import collection_exists, index_schema_docs


def setup_rag_for_database(
    server_name: str,
    database_name: str,
    db_url: str,
    force_reindex: bool = False,
) -> dict:
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
    return (
        graph_exists(server_name, database_name)
        and collection_exists(server_name, database_name)
    )




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