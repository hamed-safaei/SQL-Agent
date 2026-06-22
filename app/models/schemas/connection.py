# from pydantic import BaseModel


# class ConnectionTest(BaseModel):
#     server: str
#     database: str

# class IndexSchemaRequest(BaseModel):
#     server: str
#     database: str
#     reindex_if_exists: bool = False



"""
Pydantic schemas for the Connection router.
"""

from pydantic import BaseModel, Field


class IndexSchemaRequest(BaseModel):
    server: str = Field(..., example="localhost")
    port: int = Field(default=5432, example=5432)
    database: str = Field(..., example="bikestores")
    username: str = Field(..., example="hamed")
    password: str = Field(..., example="****")
    reindex_if_exists: bool = Field(
        default=False,
        description="اگر True باشد، حتی در صورت وجود ایندکس، دوباره ساخته می‌شود.",
    )