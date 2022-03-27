from typing import Dict, List
import datetime
from sqlalchemy import func
from sqlalchemy.sql import text
import logging

import app.db.db as db
from app.config import config
from app.db.models import Match, StaleDateTime

logger = logging.getLogger('elo')
logger.setLevel(config.settings['log_level'])
handler = logging.FileHandler(filename=config.settings['log_path'], encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_elo(team_id: int, match_datetime: datetime) -> float:
    base_elo = 1000
    session = db.get_session()

    with session() as session:
        # TODO ORM
        sql = text('SELECT SUM(change) + :b_elo as elo '
                   'FROM ( '
                   'SELECT w.winner_change as change '
                   'FROM match_elo as w '
                   'WHERE (w.winning_team = :t_id AND w.match_datetime <= :m_dt) '
                   'UNION '
                   'SELECT l.loser_change as change '
                   'FROM match_elo as l '
                   'WHERE (l.losing_team = :t_id AND l.match_datetime <= :m_dt) '
                   ')')
        elo = session.execute(sql, {'t_id': team_id, 'm_dt': match_datetime, 'b_elo': base_elo}).first().elo
        if elo is None:
            elo = base_elo
        logger.debug(elo)
        session.close()

    return elo


def calc_win_probability(team_a_elo: float, team_b_elo: float) -> float:
    #  https://en.wikipedia.org/wiki/Elo_rating_system
    alg = 400.0
    return 1 / (1 + pow(10, (team_b_elo - team_a_elo) / alg))


def calc_elo(winner_elo: float, loser_elo: float) -> (float, float):
    k = 16.0
    expected_winner_probability = calc_win_probability(loser_elo, winner_elo)
    expected_loser_probability = calc_win_probability(winner_elo, loser_elo)

    winner_change = (k * (1 - expected_winner_probability))
    loser_change = (k * (-expected_loser_probability))

    return winner_change, loser_change


def calc_match_probability(team_a_id: int, team_b_id: int, match_datetime: datetime) -> Dict:
    team_a_elo = get_elo(team_id=team_a_id, match_datetime=match_datetime)
    team_b_elo = get_elo(team_id=team_b_id, match_datetime=match_datetime)

    logger.debug("--------calc_match_probability-------------")
    logger.debug("match_datetime={}".format(match_datetime))
    logger.debug("team_a_elo={}".format(team_a_elo))
    logger.debug("team_b_elo={}".format(team_b_elo))

    return {
        'team_a': calc_win_probability(team_a_elo, team_b_elo),
        'team_b': calc_win_probability(team_b_elo, team_a_elo),
        'match_datetime': match_datetime
    }


def calc_matches_changes(matches: List[Match]):
    team_elo = {}  # store teams as through matches
    logger.debug("--------calc_matches_changes-------------")
    for match in matches:
        logger.debug("******for match in matches**********")
        logger.debug("match.match_datetime={}".format(match.match_datetime))
        winning_team_elo = get_elo(match.winning_team, match.match_datetime)
        losing_team_elo = get_elo(match.losing_team, match.match_datetime)
        if match.winning_team in team_elo.keys():  # if winning already has an elo
            winning_team_elo = team_elo[match.winning_team]
        if match.losing_team in team_elo.keys():  # if losing already has an elo
            losing_team_elo = team_elo[match.losing_team]
        logger.debug("winning_team_elo={}".format(winning_team_elo))
        logger.debug("losing_team_elo={}".format(losing_team_elo))

        match.winner_change, match.loser_change = calc_elo(winning_team_elo, losing_team_elo)
        logger.debug("match.winner_change={}".format(match.winner_change))
        logger.debug("match.loser_change={}".format(match.loser_change))
        team_elo[match.winning_team] = winning_team_elo + match.winner_change
        team_elo[match.losing_team] = losing_team_elo + match.loser_change
        logger.debug("team_elo[match.winning_team]={}".format(team_elo[match.winning_team]))
        logger.debug("team_elo[match.losing_team]={}".format(team_elo[match.losing_team]))

        logger.debug("team_elo={}".format(team_elo))


def update_matches_elo():
    session = db.get_session()

    with session() as session:
        max_stale_datetime = session.query(
            func.min(StaleDateTime.stale_datetime).label("stale_datetime")).first().stale_datetime
        if max_stale_datetime is not None:  # if there is a stale datetime
            # get all the matches we need to calc
            matches = session.query(Match) \
                .where(Match.match_datetime >= max_stale_datetime) \
                .order_by(Match.match_datetime.asc()) \
                .all()
            calc_matches_changes(matches)
            session.flush()
            session.query(StaleDateTime).delete()  # remove all stale datetimes
        session.commit()
        session.close()
