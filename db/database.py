import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, URL

load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT", "5432")

required_vars = {
    "DB_USERNAME": db_username,
    "DB_PASSWORD": db_password,
    "DB_HOST": db_host,
    "DB_NAME": db_name,
    "DB_PORT": db_port
}

missing = [key for key, value in required_vars.items() if not value]
if missing:
    raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing)}")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=db_username,
    password=db_password,
    host=db_host,
    port=int(db_port),
    database=db_name,
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()