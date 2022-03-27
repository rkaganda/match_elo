import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import logging

from app.config import config

logger = logging.getLogger('elo')
logger.setLevel(config.settings['log_level'])
handler = logging.FileHandler(filename=config.settings['log_path'], encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

Base = declarative_base()


def get_session() -> sessionmaker:
    engine = sqla.create_engine(config.settings['db_url'])
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return sessionmaker(engine)










