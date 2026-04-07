from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from db.database import Base
from models.stock import CurrencyEnum


class DailyQuote(Base):
    __tablename__ = "daily_quote"

    id_daily_quote = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_stock = Column(Integer, ForeignKey("stock.id_stock"), nullable=False, index=True)

    quote_date = Column(Date, nullable=False, index=True)

    open_price = Column(Numeric(12, 4), nullable=False)
    high_price = Column(Numeric(12, 4), nullable=False)
    low_price = Column(Numeric(12, 4), nullable=False)
    close_price = Column(Numeric(12, 4), nullable=False)
    volume = Column(BigInteger, nullable=True)

    currency = Column(
        Enum(CurrencyEnum, name="currency_enum"),
        nullable=False,
        default=CurrencyEnum.EUR,
    )

    variation_pct = Column(Numeric(8, 4), nullable=True)
    source = Column(String(30), nullable=False)

    stock = relationship("Stock", back_populates="daily_quotes")

    __table_args__ = (
        UniqueConstraint("id_stock", "quote_date", name="uq_daily_quote_stock_date"),
    )