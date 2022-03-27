from sqlalchemy import Column, Integer, Float, DateTime

from app.db.db import Base


class Match(Base):
    __tablename__ = "match_elo".format()
    match_id = Column(Integer, primary_key=True)
    match_datetime = Column(DateTime(timezone=True), nullable=False)
    winning_team = Column(Integer, nullable=False)
    losing_team = Column(Integer, nullable=False)
    winner_change = Column(Float)
    loser_change = Column(Float)


class StaleDateTime(Base):
    __tablename__ = "stale_datetimes".format()
    id = Column(Integer, primary_key=True, autoincrement=True)
    stale_datetime = Column(DateTime(timezone=True), nullable=False)

