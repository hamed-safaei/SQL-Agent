"""
app.rag — Retrieval-Augmented Generation layer.

Public surface:
  - setup_rag_for_database  : one-call setup (graph + vector)
  - is_database_indexed     : health-check
  - sync_schema_graph       : Neo4j sync only
  - index_schema_docs       : Qdrant indexing only
  - get_shortest_path       : FK path query
  - TABLE_DOCS              : raw table documentation list
"""

from app.rag.graph_store import get_shortest_path, sync_schema_graph
from app.rag.indexer import is_database_indexed, setup_rag_for_database
from app.rag.schema_docs import TABLE_DOCS
from app.rag.vector_store import index_schema_docs

__all__ = [
    "setup_rag_for_database",
    "is_database_indexed",
    "sync_schema_graph",
    "index_schema_docs",
    "get_shortest_path",
    "TABLE_DOCS",
]