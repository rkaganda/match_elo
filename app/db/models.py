from sqlalchemy import Column, Integer, Float, DateTime

from app.db.db import Base
from app.config import config


class Match(Base):
    __tablename__ = "{}_match".format(config.settings['db_prefix'])
    match_id = Column(Integer, primary_key=True)
    match_datetime = Column(DateTime(timezone=True), nullable=False)
    winning_team = Column(Integer, nullable=False)
    losing_team = Column(Integer, nullable=False)
    winner_change = Column(Float)
    loser_change = Column(Float)


class StaleDateTime(Base):
    __tablename__ = "{}_stale_datetimes".format(config.settings['db_prefix'])
    id = Column(Integer, primary_key=True, autoincrement=True)
    stale_datetime = Column(DateTime(timezone=True), nullable=False)

