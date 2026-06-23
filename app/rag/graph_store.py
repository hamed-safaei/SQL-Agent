"""
Graph store operations using Neo4j.
Syncs PostgreSQL foreign-key relationships as a property graph.
"""

import psycopg2
from neo4j import GraphDatabase

from app.core import settings

_driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASS),
)

_FK_QUERY = """
SELECT
    src_ns.nspname || '.' || src.relname AS source_table,
    tgt_ns.nspname || '.' || tgt.relname AS target_table
FROM pg_constraint c
JOIN pg_class     src    ON src.oid = c.conrelid
JOIN pg_namespace src_ns ON src_ns.oid = src.relnamespace
JOIN pg_class     tgt    ON tgt.oid = c.confrelid
JOIN pg_namespace tgt_ns ON tgt_ns.oid = tgt.relnamespace
WHERE c.contype = 'f'
"""


# -------------------------------------------------------------------------------





def _graph_id(server_name: str, database_name: str) -> str:
    return (
        f"{server_name}_{database_name}"
        .lower()
        .replace(" ", "_")
        .replace(".", "_")
        .replace("-", "_")
    )


def _fetch_fks(db_url: str) -> list[tuple[str, str]]:
    """Extract all foreign-key pairs from a PostgreSQL database."""
    with psycopg2.connect(db_url) as conn, conn.cursor() as cur:
        cur.execute(_FK_QUERY)
        return cur.fetchall()


# ----------------------------------------------------------------------------------


def graph_exists(server_name: str, database_name: str) -> bool:
    """Return True if at least one Table node exists for this graph."""
    gid = _graph_id(server_name, database_name)
    with _driver.session() as session:
        result = session.run(
            "MATCH (t:Table {graph_id: $gid}) RETURN COUNT(t) AS n",
            gid=gid,
        )
        return result.single()["n"] > 0


def sync_schema_graph(
    server_name: str,
    database_name: str,
    db_url: str,
    reindex_if_exists: bool = False,
) -> dict:
    """
    Sync PostgreSQL FK relationships into Neo4j.
    Creates the graph on first run; merges changes on subsequent runs.

    Args:
        reindex_if_exists:
            False → skip immediately if graph already exists (default).
            True  → re-fetch FKs and merge even if graph exists.

    Returns:
        Dict with graph_id, tables_count, relations_count (or status if skipped).
    """
    gid = _graph_id(server_name, database_name)

    if not reindex_if_exists and graph_exists(server_name, database_name):
        return {
            "graph_id": gid,
            "tables_count": 0,
            "relations_count": 0,
            "status": "skipped",
            "message": "Graph already exists.",
        }

    fks = _fetch_fks(db_url)
    tables = {table for pair in fks for table in pair}

    with _driver.session() as session:
        for table_name in tables:
            session.run(
                """
                MERGE (t:Table {graph_id: $gid, name: $name})
                SET t.server   = $server,
                    t.database = $database
                """,
                gid=gid,
                name=table_name,
                server=server_name,
                database=database_name,
            )

        for src, tgt in fks:
            session.run(
                """
                MATCH (a:Table {graph_id: $gid, name: $src})
                MATCH (b:Table {graph_id: $gid, name: $tgt})
                MERGE (a)-[:FK]->(b)
                """,
                gid=gid,
                src=src,
                tgt=tgt,
            )

    return {
        "graph_id": gid,
        "tables_count": len(tables),
        "relations_count": len(fks),
    }




# ----------------------------------------------------------------------------------



def get_shortest_path(
    server_name: str,
    database_name: str,
    src: str,
    tgt: str,
) -> list[str] | None:

    gid = _graph_id(server_name, database_name)
    with _driver.session() as session:
        result = session.run(
            """
            MATCH p = shortestPath(
                (a:Table {graph_id: $gid, name: $src})
                -[:FK*]-
                (b:Table {graph_id: $gid, name: $tgt})
            )
            RETURN [n IN nodes(p) | n.name] AS path
            """,
            gid=gid,
            src=src,
            tgt=tgt,
        )
        record = result.single()
        return record["path"] if record else None