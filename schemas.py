"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# -------- Financial Literacy Game Schemas --------

class Holding(BaseModel):
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type, e.g., stock, real_estate, business, cash")
    value: float = Field(0, ge=0, description="Current market value")
    income: float = Field(0, description="Recurring monthly income from this asset")

class Debt(BaseModel):
    name: str = Field(..., description="Liability name")
    type: str = Field(..., description="Liability type, e.g., mortgage, loan, credit")
    balance: float = Field(0, ge=0, description="Outstanding balance")
    payment: float = Field(0, ge=0, description="Recurring monthly payment")

class Player(BaseModel):
    """
    Players collection schema
    Collection name: "player"
    """
    name: str = Field(..., description="Player display name")
    profession: str = Field(..., description="Chosen profession archetype")
    income: float = Field(0, ge=0, description="Total monthly earned income")
    expenses: float = Field(0, ge=0, description="Total monthly expenses (excluding liability payments)")
    cash: float = Field(0, description="Liquid cash on hand")
    assets: List[Holding] = Field(default_factory=list, description="List of assets")
    liabilities: List[Debt] = Field(default_factory=list, description="List of liabilities")

class MarketEvent(BaseModel):
    asset_type: str
    percent_change: float
    message: str

# Example schemas kept for reference (not used by the app directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
