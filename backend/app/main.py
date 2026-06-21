from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import Base, SessionLocal, engine, get_db, settings
from app.models import Company, Job, Post, Profile
from app.schemas import CompanyOut, FeedPostOut, JobCreate, JobOut, PostCreate, ProfileCreate, ProfileOut
from app.seed import seed_if_empty

app = FastAPI(title="Mini Professional Network API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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


@app.post("/api/profiles", response_model=ProfileOut, status_code=201)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)) -> Profile:
    db_profile = Profile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@app.post("/api/posts", response_model=FeedPostOut, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)) -> Post:
    author = db.get(Profile, post.author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    db_post = Post(author_id=post.author_id, body=post.body)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/api/companies", response_model=list[CompanyOut])
def get_companies(db: Session = Depends(get_db)) -> list[Company]:
    return list(db.scalars(select(Company).order_by(Company.name)))


@app.get("/api/jobs", response_model=list[JobOut])
def get_jobs(db: Session = Depends(get_db)) -> list[Job]:
    statement = select(Job).options(joinedload(Job.company)).order_by(Job.role)
    return list(db.scalars(statement))


@app.post("/api/jobs", response_model=JobOut, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)) -> Job:
    company = db.scalar(select(Company).where(Company.name == job.company_name))

    if company is None:
        company = Company(
            name=job.company_name,
            industry=job.company_industry,
            logo_url=job.company_logo_url,
        )
        db.add(company)
        db.flush()

    db_job = Job(
        company_id=company.id,
        role=job.role,
        location=job.location,
        work_mode=job.work_mode,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
