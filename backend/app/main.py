from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import Base, SessionLocal, engine, get_db, settings
from app.models import Company, Job, Post, Profile
from app.schemas import CompanyOut, FeedPostOut, JobOut, ProfileOut
from app.seed import seed_if_empty

app = FastAPI(title="Mini Professional Network API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/api/feed", response_model=list[FeedPostOut])
def get_feed(db: Session = Depends(get_db)) -> list[Post]:
    statement = select(Post).options(joinedload(Post.author)).order_by(Post.created_at.desc())
    return list(db.scalars(statement))


@app.get("/api/profiles", response_model=list[ProfileOut])
def get_profiles(db: Session = Depends(get_db)) -> list[Profile]:
    return list(db.scalars(select(Profile).order_by(Profile.name)))


@app.get("/api/companies", response_model=list[CompanyOut])
def get_companies(db: Session = Depends(get_db)) -> list[Company]:
    return list(db.scalars(select(Company).order_by(Company.name)))


@app.get("/api/jobs", response_model=list[JobOut])
def get_jobs(db: Session = Depends(get_db)) -> list[Job]:
    statement = select(Job).options(joinedload(Job.company)).order_by(Job.role)
    return list(db.scalars(statement))
