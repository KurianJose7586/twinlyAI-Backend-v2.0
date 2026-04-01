# app/schemas/bot.py

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from .pyobjectid import PyObjectId
from bson import ObjectId
from datetime import datetime

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    link: Optional[str] = None


class BotBase(BaseModel):
    name: str

class BotCreate(BotBase):
    pass

# --- UPDATED BotUpdate MODEL ---
class BotUpdate(BaseModel):
    name: Optional[str] = None #<-- Make name optional
    # --- NEW FIELDS ---
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    avatar_url: Optional[str] = None
    # --- SOCIAL LINKS ---
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    projects: Optional[List[Project]] = None
    # ------------------

class Bot(BotBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[str] = None
    # --- NEW FIELDS ---
    summary: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[float] = 0.0
    avatar_url: Optional[str] = None
    # --- SOCIAL LINKS ---
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    projects: Optional[List[Project]] = []
    # ------------------

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True


# ── Conversation / History schemas ───────────────────────────────────────────

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None


class ConversationCreate(BaseModel):
    bot_id: str
    recruiter_id: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_company: Optional[str] = None
    recruiter_email: Optional[str] = None
    messages: List[ConversationMessage] = []


class Conversation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    bot_id: str
    recruiter_id: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_company: Optional[str] = None
    recruiter_email: Optional[str] = None
    messages: List[ConversationMessage] = []
    message_count: int = 0
    duration_seconds: int = 0
    summary: Optional[str] = None
    status: Literal["qualified", "cold", "followup", "ghosted"] = "cold"
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True


# ── Resume version schemas ────────────────────────────────────────────────────

class ResumeVersion(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    bot_id: str
    user_id: str
    filename: str
    uploaded_at: datetime
    is_active: bool = True
    version_number: int = 1

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True


# ── Activity event schemas ────────────────────────────────────────────────────

class ActivityEvent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    bot_id: Optional[str] = None
    event_type: Literal["chat", "resume", "profile"]
    title: str
    detail: Optional[str] = None
    ref_id: Optional[str] = None   # conversation_id or resume_version_id
    created_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True