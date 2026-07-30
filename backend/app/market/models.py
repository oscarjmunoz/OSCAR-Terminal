from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class MarketSnapshot(Base):

    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        index=True,
    )

    bid: Mapped[float] = mapped_column(
        Float,
    )

    ask: Mapped[float] = mapped_column(
        Float,
    )

    spread: Mapped[float] = mapped_column(
        Float,
    )

    timestamp: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )