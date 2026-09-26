import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Pulled from environment variables rather than hardcoded, so the same
# code runs unchanged whether it's pointed at RDS in AWS or a local MySQL
# for testing. DB_HOST should be just the hostname part of the RDS
# endpoint output (Terraform's rds_endpoint output includes ":3306" —
# strip that off, or set DB_PORT separately as done here).
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ.get("DB_NAME", "order_tracking")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# pool_pre_ping checks a connection is still alive before handing it to a
# request — protects against RDS silently closing idle connections, which
# would otherwise surface as a confusing mid-request error.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: one DB session per request, always closed after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
