import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

app = FastAPI(title="Event Organizing Company API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health and info
@app.get("/")
def read_root():
    return {"message": "Event Organizing Company Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# Database helpers
from database import db, create_document, get_documents
from schemas import Service, TeamMember, Inquiry

# Utility

def to_str_id(doc: dict):
    if doc and doc.get("_id"):
        doc["id"] = str(doc.pop("_id"))
    return doc

# Public content endpoints
@app.get("/api/services")
def list_services():
    try:
        items = get_documents("service", {}, None)
        return [to_str_id(d) for d in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/team")
def list_team(team: Optional[str] = None):
    try:
        query = {"team": team} if team else {}
        items = get_documents("teammember", query, None)
        return [to_str_id(d) for d in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inquiries
class InquiryPayload(Inquiry):
    pass

@app.post("/api/inquiries")
def create_inquiry(payload: InquiryPayload):
    try:
        _id = create_document("inquiry", payload)
        return {"id": _id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
