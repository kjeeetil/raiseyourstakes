import os
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _database_url() -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Build a Cloud SQL Unix socket connection string if details are provided.
    cloud_sql_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD", "")
    if cloud_sql_name and db_name and db_user:
        host = quote_plus(os.getenv("DB_HOST", f"/cloudsql/{cloud_sql_name}"))
        password = f":{quote_plus(db_password)}" if db_password else ""
        return f"postgresql+psycopg2://{quote_plus(db_user)}{password}@/{quote_plus(db_name)}?host={host}"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DATA_DIR / 'app.db'}"


DATABASE_URL = _database_url()
parsed_url = make_url(DATABASE_URL)
connect_args = {"check_same_thread": False} if parsed_url.drivername.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    if parsed_url.drivername.startswith("sqlite"):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
