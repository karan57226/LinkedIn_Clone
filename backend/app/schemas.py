from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


DEFAULT_AVATAR_URL = (
    "https://images.unsplash.com/photo-1517841905240-472988babdf9"
    "?w=160&h=160&fit=crop&crop=faces"
)
DEFAULT_COMPANY_LOGO_URL = (
    "https://images.unsplash.com/photo-1497366754035-f200968a6e72"
    "?w=160&h=160&fit=crop"
)


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=160)
    location: str = Field(min_length=1, max_length=120)
    avatar_url: str = DEFAULT_AVATAR_URL


class PostCreate(BaseModel):
    author_id: int
    body: str = Field(min_length=1)


class JobCreate(BaseModel):
    role: str = Field(min_length=1, max_length=160)
    location: str = Field(min_length=1, max_length=120)
    work_mode: str = Field(min_length=1, max_length=40)
    company_name: str = Field(min_length=1, max_length=140)
    company_industry: str = Field(default="Technology", min_length=1, max_length=120)
    company_logo_url: str = DEFAULT_COMPANY_LOGO_URL


class ProfileOut(BaseModel):
    id: int
    name: str
    title: str
    location: str
    avatar_url: str

    model_config = ConfigDict(from_attributes=True)


class CompanyOut(BaseModel):
    id: int
    name: str
    industry: str
    logo_url: str

    model_config = ConfigDict(from_attributes=True)


class FeedPostOut(BaseModel):
    id: int
    body: str
    created_at: datetime
    author: ProfileOut

    model_config = ConfigDict(from_attributes=True)


class JobOut(BaseModel):
    id: int
    role: str
    location: str
    work_mode: str
    company: CompanyOut

    model_config = ConfigDict(from_attributes=True)
