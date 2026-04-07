from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from db.database import Base

class LiveQuote(Base):
    __tablename__ = "live_quote"

    id_live_quote = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_stock = Column(Integer, ForeignKey("stock.id_stock"), nullable=False, index=True)

    collected_at = Column(DateTime, nullable=False, index=True)

    last_price = Column(Numeric(12, 4), nullable=False)
    open_price = Column(Numeric(12, 4), nullable=True)
    high_price = Column(Numeric(12, 4), nullable=True)
    low_price = Column(Numeric(12, 4), nullable=True)
    volume = Column(BigInteger, nullable=True)
    variation_pct = Column(Numeric(8, 4), nullable=True)

    stock = relationship("Stock", back_populates="live_quotes")