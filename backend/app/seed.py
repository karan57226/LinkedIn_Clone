from sqlalchemy.orm import Session

from app.models import Company, Job, Post, Profile


def seed_if_empty(db: Session) -> None:
    if db.query(Profile).first():
        return

    profiles = [
        Profile(
            name="Maya Chen",
            title="Cloud Platform Engineer",
            location="Sydney, NSW",
            avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=160&h=160&fit=crop&crop=faces",
        ),
        Profile(
            name="Noah Patel",
            title="Product Manager, Developer Tools",
            location="Melbourne, VIC",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=160&h=160&fit=crop&crop=faces",
        ),
        Profile(
            name="Ava Williams",
            title="Backend Engineer",
            location="Brisbane, QLD",
            avatar_url="https://images.unsplash.com/photo-1544723795-3fb6469f5b39?w=160&h=160&fit=crop&crop=faces",
        ),
    ]

    companies = [
        Company(
            name="HarbourStack",
            industry="Cloud Infrastructure",
            logo_url="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=160&h=160&fit=crop",
        ),
        Company(
            name="Northstar Analytics",
            industry="Data Platforms",
            logo_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=160&h=160&fit=crop",
        ),
    ]

    db.add_all(profiles + companies)
    db.flush()

    db.add_all(
        [
            Post(
                author_id=profiles[0].id,
                body="Finished migrating our internal API to private subnets behind an application load balancer. Security groups finally feel less mysterious.",
            ),
            Post(
                author_id=profiles[1].id,
                body="The best onboarding docs explain why the system exists before they explain how to run it.",
            ),
            Post(
                author_id=profiles[2].id,
                body="Tuning SQLAlchemy queries today. The database is usually polite enough to tell you what hurts if you ask with EXPLAIN.",
            ),
            Job(
                company_id=companies[0].id,
                role="Junior Cloud Engineer",
                location="Sydney, NSW",
                work_mode="Hybrid",
            ),
            Job(
                company_id=companies[1].id,
                role="Python Backend Developer",
                location="Remote Australia",
                work_mode="Remote",
            ),
        ]
    )
    db.commit()
