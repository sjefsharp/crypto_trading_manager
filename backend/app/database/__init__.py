"""
Database initialization module
"""

from app.core.database import engine
from app.models.database_models import Base

__all__ = ["Base", "init_db"]


def init_db() -> None:
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
