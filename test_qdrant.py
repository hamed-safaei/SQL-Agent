from fastapi import FastAPI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid

app = FastAPI()

# اتصال به Qdrant
client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "test_collection"


# ساخت collection اگر نبود
def create_collection():
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=4,  # چون embedding fake می‌سازیم
                distance=Distance.COSINE
            )
        )


create_collection()


# یک embedding fake برای تست
def fake_embedding(text: str):
    # فقط برای تست (واقعی نیست)
    return [float(len(text)), 0.1, 0.2, 0.3]


@app.post("/insert")
def insert(text: str):

    vector = fake_embedding(text)

    point_id = str(uuid.uuid4())

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"text": text}
            )
        ]
    )

    return {
        "status": "saved",
        "id": point_id,
        "vector": vector
    }