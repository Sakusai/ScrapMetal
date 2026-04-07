import enum

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class CurrencyEnum(enum.Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"


class Stock(Base):
    __tablename__ = "stock"

    id_stock = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ticker = Column(String(50), nullable=False, unique=True, index=True)
    label = Column(String(255), nullable=False, index=True)
    boursorama_url = Column(String(500), nullable=True)
    currency = Column(
        Enum(CurrencyEnum, name="currency_enum"),
        nullable=False,
        default=CurrencyEnum.EUR,
    )

    live_quotes = relationship(
        "LiveQuote",
        back_populates="stock",
        cascade="all, delete-orphan",
    )

    daily_quotes = relationship(
        "DailyQuote",
        back_populates="stock",
        cascade="all, delete-orphan",
    )