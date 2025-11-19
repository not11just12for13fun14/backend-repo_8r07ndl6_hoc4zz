import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Property, Inquiry

app = FastAPI(title="Real Estate Listing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_public_id(doc):
    if not doc:
        return doc
    d = dict(doc)
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    # Convert any datetime to isoformat string for JSON cleanliness
    for key, val in list(d.items()):
        try:
            import datetime
            if isinstance(val, (datetime.datetime, datetime.date)):
                d[key] = val.isoformat()
        except Exception:
            pass
    return d


@app.get("/")
def read_root():
    return {"message": "Real Estate API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:60]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:60]}"
    return response


# Properties
@app.get("/api/properties", response_model=List[dict])
def list_properties(limit: Optional[int] = 20):
    docs = get_documents("property", {}, limit)
    return [to_public_id(doc) for doc in docs]


@app.get("/api/properties/{property_id}")
def get_property(property_id: str):
    try:
        doc = db["property"].find_one({"_id": ObjectId(property_id)})
    except Exception:
        doc = None
    if not doc:
        raise HTTPException(status_code=404, detail="Property not found")
    return to_public_id(doc)


@app.post("/api/properties")
def create_property(payload: Property):
    new_id = create_document("property", payload)
    doc = db["property"].find_one({"_id": ObjectId(new_id)})
    return to_public_id(doc)


# Inquiries
class InquiryIn(BaseModel):
    property_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = "website"


@app.post("/api/inquiries")
def create_inquiry(payload: InquiryIn):
    # If property_id exists, ensure it's valid but don't fail hard if not provided
    if payload.property_id:
        try:
            _ = ObjectId(payload.property_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid property_id")

    new_id = create_document("inquiry", payload.model_dump())
    return {"id": new_id, "status": "received"}


# Seeder endpoint to quickly add a sample property
@app.post("/api/seed")
def seed_sample_property():
    sample = Property(
        title="Modern Craftsman with Valley Views",
        address="1234 Maple Ridge Dr",
        city="San Jose",
        state="CA",
        zipcode="95120",
        price=1495000,
        status="For Sale",
        beds=4,
        baths=3.5,
        sqft=2650,
        lot_size=0.25,
        year_built=2016,
        property_type="Single Family",
        hoa_fee=85.0,
        price_per_sqft=564.15,
        days_on_market=3,
        photos=[
            "https://images.unsplash.com/photo-1600585154526-990dced4db0d",
            "https://images.unsplash.com/photo-1560185127-6ed189bf02f4",
            "https://images.unsplash.com/photo-1560448075-bb4caa6c0f11",
            "https://images.unsplash.com/photo-1505691723518-36a5ac3b2d95"
        ],
        description=(
            "This sun‑filled craftsman blends modern amenities with timeless charm. "
            "Wide-plank floors, chef’s kitchen with quartz counters, and an indoor/outdoor layout "
            "that flows to a flat backyard and pergola. Primary suite with balcony and spa bath."
        ),
        features=[
            "Chef’s kitchen with 36\" range",
            "Walk-in pantry",
            "Vaulted great room",
            "Upstairs laundry",
            "EV-ready garage",
            "Owned solar",
            "Dual-zone HVAC",
            "Smart irrigation"
        ],
        latitude=37.227,
        longitude=-121.89,
        schools=[
            "Williams Elementary (9/10)",
            "Bret Harte Middle (8/10)",
            "Leland High (10/10)"
        ],
        open_house=[
            "Sat 1–4 PM",
            "Sun 12–3 PM"
        ],
        agent_name="Alex Morgan",
        agent_phone="(408) 555-0133",
        agent_email="alex@example.com",
    )
    new_id = create_document("property", sample)
    doc = db["property"].find_one({"_id": ObjectId(new_id)})
    return to_public_id(doc)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
