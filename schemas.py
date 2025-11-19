"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class Property(BaseModel):
    """
    Real estate listing
    Collection name: "property"
    """
    # Basics
    title: str = Field(..., description="Marketing title for the property")
    address: str = Field(..., description="Full street address")
    city: str
    state: str
    zipcode: str
    price: int = Field(..., ge=0)
    status: str = Field("For Sale", description="For Sale, Pending, Sold, etc.")

    # Specs
    beds: float = Field(..., ge=0)
    baths: float = Field(..., ge=0)
    sqft: int = Field(..., ge=0, description="Interior square footage")
    lot_size: Optional[float] = Field(None, description="Lot size in acres")
    year_built: Optional[int] = Field(None)
    property_type: Optional[str] = Field(None, description="Single Family, Condo, Townhouse, etc.")
    hoa_fee: Optional[float] = Field(None, description="Monthly HOA fee")
    price_per_sqft: Optional[float] = Field(None)
    days_on_market: Optional[int] = Field(None)

    # Media
    photos: List[HttpUrl] = Field(default_factory=list)
    video_url: Optional[HttpUrl] = None
    virtual_tour_url: Optional[HttpUrl] = None

    # Description & features
    description: Optional[str] = None
    features: List[str] = Field(default_factory=list)

    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Schools (basic summary like Zillow/Redfin show)
    schools: List[str] = Field(default_factory=list, description="Nearby schools summary lines")

    # Open house
    open_house: List[str] = Field(default_factory=list, description="Human-readable schedule lines")

    # Agent / contact
    agent_name: Optional[str] = None
    agent_phone: Optional[str] = None
    agent_email: Optional[str] = None

    # Meta
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Inquiry(BaseModel):
    """
    Buyer inquiries captured from the contact form
    Collection name: "inquiry"
    """
    property_id: Optional[str] = Field(None, description="Related property document id")
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = Field("website", description="lead source")
    created_at: Optional[datetime] = None

