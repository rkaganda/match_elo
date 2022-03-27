from typing import Dict

import sqlalchemy.exc

import app.db.db as db
import app.src.elo as elo
from app.db.models import Match, StaleDateTime
import logging
from app.config import config


logger = logging.getLogger('elo')
logger.setLevel(config.settings['log_level'])
handler = logging.FileHandler(filename=config.settings['log_path'], encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class AddMatchFailed(Exception):
    def __init__(self, message):
        super().__init__(message)


def add_match(match_data: Dict, update_elo=False) -> Dict:
    session = db.get_session()

    try:
        with session() as session:
            match = Match(**match_data)  # new match to add
            session.add(StaleDateTime(stale_datetime=match_data['match_datetime']))  # add state dt
            session.add(match)  # add match
            session.commit()
            session.close()
    except sqlalchemy.exc.IntegrityError as e:
        raise AddMatchFailed(e)

    return get_match(match_data['match_id'], update_elo)


def get_match(match_id: int, update_elo=False) -> Dict:
    if update_elo:
        elo.update_matches_elo()

    session = db.get_session()
    with session() as session:
        match_data = session.query(Match).where(Match.match_id == match_id).first()
        session.close()

    if match_data is not None:
        match_data = match_data.__dict__
        if '_sa_instance_state' in match_data:  # remove orm stuff
            del match_data['_sa_instance_state']
    else:
        match_data = {}

    return match_data


def delete_match(match_id: int, update_elo=False) -> Dict:
    session = db.get_session()

    with session() as session:
        session.query(Match).where(Match.match_id == match_id).delete()
        session.commit()
        session.close()

    return get_match(match_id, update_elo)


def update_match(match_data: Dict):
    session = db.get_session()

    with session() as session:
        match = session.query(Match).where(Match.match_id == match_data['match_id']).first()
        for key, value in match_data.items():
            setattr(match, key, value)
        session.commit()
        session.close()