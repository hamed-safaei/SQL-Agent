from pydantic import BaseModel


class ConnectionTest(BaseModel):

    server: str

    database: str