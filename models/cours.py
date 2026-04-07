from sqlalchemy import Column, Integer, String
from db.database import Base

class Cours(Base):
    __tablename__ = "cours"

    id_cours = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
