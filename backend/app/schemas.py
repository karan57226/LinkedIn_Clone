from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
