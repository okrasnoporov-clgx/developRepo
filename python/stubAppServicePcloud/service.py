import os
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Body
# pyrefly: ignore [missing-import]
import pymongo

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "stub_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "records")

client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


@app.get("/alpha/v1/info", tags=["Service info"])
def get_info():
    return {"service": "alpha", "status": "ok", "server": "FastAPI"}


@app.post("/db/v1/record", tags=["Database"])
def create_record(payload: Dict[str, Any] = Body(...)):
    if not isinstance(payload, dict) or not payload or len(payload) > 20:
        raise HTTPException(
            status_code=400,
            detail="Payload must be a non-empty JSON object with no more than 20 fields."
        )

    doc = payload.copy()
    try:
        result = collection.insert_one(doc)
        inserted_id = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to insert record into MongoDB: {str(e)}"
        )

    return {
        "status": "success",
        "inserted_id": inserted_id,
        "fields_count": len(payload)
    }

