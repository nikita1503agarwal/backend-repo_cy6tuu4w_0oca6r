import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Player, MarketEvent

app = FastAPI(title="Financial Literacy Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Financial Literacy Game Backend Running"}

# --- Schema exposure for admin/tools ---
class SchemaExpose(BaseModel):
    name: str
    fields: dict

@app.get("/schema", response_model=List[SchemaExpose])
def get_schema():
    return [
        {"name": "player", "fields": Player.model_json_schema()},
    ]

# --- Core Game Endpoints ---

@app.post("/api/players", response_model=dict)
def create_player(player: Player):
    try:
        inserted_id = create_document("player", player)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/players", response_model=List[dict])
def list_players(limit: Optional[int] = 50):
    try:
        docs = get_documents("player", {}, limit)
        # Convert ObjectId to string if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/markets/snapshot")
def market_snapshot():
    """Return a simple static snapshot to drive UI for now."""
    return {
        "stocks": {"index": 4120.5, "change": 0.8},
        "property": {"avg_price": 356000, "change": -0.4},
        "business": {"sentiment": 62},
        "credit": {"rate": 6.9}
    }

@app.post("/api/markets/tick", response_model=MarketEvent)
def market_tick():
    """Generate a pseudo-random market event. Deterministic for demo."""
    import random
    events = [
        ("stock", 2.4, "Tech rally lifts equities"),
        ("real_estate", -1.2, "Mortgage rate uptick cools housing"),
        ("business", 1.0, "Local small biz tax credit announced"),
        ("cash", 0.1, "Savings interest accrues")
    ]
    e = random.choice(events)
    return MarketEvent(asset_type=e[0], percent_change=e[1], message=e[2])

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
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
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
