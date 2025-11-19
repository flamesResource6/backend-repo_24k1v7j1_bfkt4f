"""
Database Schemas for Event Organizing Company

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Service(BaseModel):
    """
    Services offered by the company
    Collection name: "service"
    """
    title: str = Field(..., description="Service title, e.g., Wedding Planning")
    description: str = Field(..., description="Short description of the service")
    category: str = Field(..., description="Category, e.g., Media, Events, Outreach")
    icon: Optional[str] = Field(None, description="Icon name for UI")
    featured: bool = Field(False, description="Whether to highlight on homepage")

class TeamMember(BaseModel):
    """
    Team members across departments
    Collection name: "teammember"
    """
    name: str = Field(..., description="Full name")
    role: str = Field(..., description="Role in the team")
    team: str = Field(..., description="Team/Department name, e.g., Media, Events, Outreach")
    bio: Optional[str] = Field(None, description="Short bio")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")

class Inquiry(BaseModel):
    """
    Client inquiries/booking requests
    Collection name: "inquiry"
    """
    name: str = Field(..., description="Client name")
    email: EmailStr = Field(..., description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    service: Optional[str] = Field(None, description="Requested service title or category")
    event_date: Optional[str] = Field(None, description="Desired event date (string)")
    budget_range: Optional[str] = Field(None, description="Budget range text")
    message: Optional[str] = Field(None, description="Additional details")

# The Flames database viewer can read these via GET /schema
SCHEMAS: List[type] = [Service, TeamMember, Inquiry]
