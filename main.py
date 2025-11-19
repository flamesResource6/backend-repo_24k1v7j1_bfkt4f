import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

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
@app.post("/api/inquiries")
def create_inquiry(payload: Inquiry):
    try:
        _id = create_document("inquiry", payload)
        return {"id": _id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: simple admin list of inquiries (limit for safety)
@app.get("/api/inquiries")
def list_inquiries(limit: int = 20):
    try:
        items = get_documents("inquiry", {}, min(max(limit, 1), 100))
        return [to_str_id(d) for d in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Seeder endpoint to populate initial data
@app.post("/api/seed")
def seed_data():
    """
    Inserts sample Services and Team members if collections are empty.
    Safe to call multiple times – only seeds when no documents exist.
    """
    try:
        collections = db.list_collection_names() if db else []
        seeded = {"service": 0, "teammember": 0}

        # Seed Services if empty
        service_empty = True
        try:
            service_empty = len(get_documents("service", {}, 1)) == 0
        except Exception:
            pass
        if service_empty:
            samples: List[Service] = [
                Service(title="Wedding Planning", description="End-to-end planning, decor, coordination", category="Events", featured=True),
                Service(title="Corporate Events", description="Conferences, summits, award nights", category="Events", featured=True),
                Service(title="Media Production", description="Photo, video, live streaming, aftermovies", category="Media"),
                Service(title="Outreach & Marketing", description="Influencers, sponsorships, community programs", category="Outreach"),
            ]
            for s in samples:
                create_document("service", s)
                seeded["service"] += 1

        # Seed Team if empty
        team_empty = True
        try:
            team_empty = len(get_documents("teammember", {}, 1)) == 0
        except Exception:
            pass
        if team_empty:
            members: List[TeamMember] = [
                TeamMember(name="Aisha Khan", role="Head of Events", team="Events"),
                TeamMember(name="Rohit Verma", role="Media Director", team="Media"),
                TeamMember(name="Sara Lee", role="Outreach Lead", team="Outreach"),
                TeamMember(name="David Chen", role="Operations Manager", team="Operations"),
            ]
            for m in members:
                create_document("teammember", m)
                seeded["teammember"] += 1

        return {"seeded": seeded}
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
