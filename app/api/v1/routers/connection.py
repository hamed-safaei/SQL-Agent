from fastapi import APIRouter
import asyncpg
import asyncio

from app.models import schemas

router = APIRouter(
    tags=["Connection"]
)


@router.post("/test-connection")
async def test_connection(conn: schemas.ConnectionTest):

    dsn = f"postgresql://{'hamed'}:{'1234'}@{conn.server}:{'5432'}/{conn.database}"

    try:
        connection = await asyncio.wait_for(
            asyncpg.connect(dsn),
            timeout=5.0
        )

        await connection.close()

        return {
            "success": True,
            "message": "اتصال با موفقیت برقرار شد ✓"
        }

    except asyncio.TimeoutError:
        return {
            "success": False,
            "message": "خطا: زمان اتصال به پایان رسید. سرور در دسترس نیست."
        }

    except asyncpg.InvalidCatalogNameError:
        return {
            "success": False,
            "message": "خطا: دیتابیس یافت نشد."
        }

    except asyncpg.InvalidAuthorizationSpecificationError:
        return {
            "success": False,
            "message": "خطا: نام کاربری یا رمز عبور اشتباه است."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"خطا در اتصال: {str(e)}"
        }