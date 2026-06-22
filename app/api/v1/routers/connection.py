import asyncio

import asyncpg
from fastapi import APIRouter, HTTPException, status

from app.models.schemas.connection import IndexSchemaRequest
from app.rag.indexer import setup_rag_for_database

router = APIRouter(tags=["Connection"])


# --------------------------------------------------------------------------- 

def _build_dsn(req: IndexSchemaRequest) -> str:
    return (
        f"postgresql://{req.username}:{req.password}"
        f"@{req.server}:{req.port}/{req.database}"
    )


async def _verify_connection(dsn: str) -> None:
    try:
        conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=5.0)
        await conn.close()

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="زمان اتصال به پایان رسید. سرور در دسترس نیست.",
        )
    except asyncpg.InvalidCatalogNameError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دیتابیس یافت نشد.",
        )
    except asyncpg.InvalidAuthorizationSpecificationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"خطا در اتصال: {exc}",
        )


# --------------------------------------------------------------------------- 

@router.post("/index-schema", status_code=status.HTTP_200_OK)
async def index_schema(req: IndexSchemaRequest):

    dsn = _build_dsn(req)

    # ── 1. Connection check ────────────────────────────────────────────────────
    await _verify_connection(dsn)

    # ── 2 + 3. Graph sync & vector indexing (concurrent) ──────────────────────
    try:
        result = await asyncio.to_thread(
            setup_rag_for_database,
            server_name=req.server,
            database_name=req.database,
            db_url=dsn,
            force_reindex=req.reindex_if_exists,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در indexing: {exc}",
        )

    return {"success": True, **result}