"""
Database initialization module
"""
from app.core.database import engine
from app.models.database_models import Base

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
