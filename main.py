import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Contact

app = FastAPI(title="3D Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "3D Portfolio backend is running"}

@app.get("/test")
def test_database():
    """Health + DB connectivity."""
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if os.getenv("DATABASE_URL"):
            status["database_url"] = "✅ Set"
        if os.getenv("DATABASE_NAME"):
            status["database_name"] = "✅ Set"

        if db is not None:
            status["database"] = "✅ Available"
            try:
                status["collections"] = db.list_collection_names()[:10]
                status["connection_status"] = "Connected"
                status["database"] = "✅ Connected & Working"
            except Exception as e:
                status["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            status["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)[:120]}"

    return status

@app.post("/contact")
def create_contact(contact: Contact):
    """Persist a contact message to MongoDB."""
    try:
        inserted_id = create_document("contact", contact)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contacts")
def list_contacts(limit: int = 20):
    try:
        docs = get_documents("contact", limit=limit)
        # Convert ObjectId to string
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
