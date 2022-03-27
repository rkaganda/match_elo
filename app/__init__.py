from flask import Flask, request, jsonify
from dateutil import parser
import logging

from app.config import config
from app.src import elo, match

logger = logging.getLogger('elo')
logger.setLevel(config.settings['log_level'])
handler = logging.FileHandler(filename=config.settings['log_path'], encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

app = Flask(__name__)


@app.route("/match", methods=['GET'])
def match_get():
    match_id = request.args.get('match_id', type=int)
    update_elo = request.form.get('update_elo') or False

    data = match.get_match(match_id, update_elo)
    if len(data) == 0:
        return jsonify(
            isError=False,
            message="Not Found",
            statusCode=404,
            data=data
        )

    return jsonify(
        isError=False,
        message="Success",
        statusCode=200,
        data=data
    )


@app.route("/match", methods=['DELETE'])
def match_delete():
    try:
        match_id = request.args.get('match_id', type=int)
        update_elo = request.form.get('update_elo') or False

        match_data = match.delete_match(match_id, update_elo)
        if len(match_data) > 0:
            raise Exception("{}".format(match_data))

        return jsonify(
            isError=False,
            message="Success",
            statusCode=204
        )
    except Exception as e:
        logger.exception(e)
        raise e


@app.route("/match", methods=['POST'])
def match_post():
    try:
        match_data = {
            'match_id': int(request.form.get('match_id', type=int)),
            'match_datetime': parser.parse(request.form.get('match_datetime', type=str)),
            'winning_team': int(request.form.get('winning_team', type=int)),
            'losing_team': int(request.form.get('losing_team', type=int)),
        }
        if match_data['winning_team'] == match_data['losing_team']:
            raise ValueError("{}={}".format(match_data['winning_team'], match_data['losing_team']))
    except ValueError as e:
        return jsonify(
            isError=True,
            message=str(e),
            statusCode=400,
            data={}
        )
    update_elo = request.form.get('update_elo') or False

    try:
        match_data = match.add_match(match_data=match_data, update_elo=update_elo)
        return jsonify(
            isError=False,
            message="Success",
            statusCode=201,
            data=match_data
        )
    except match.AddMatchFailed as e:
        return jsonify(
            isError=True,
            message='AddMatchFailed',
            statusCode=409,
            data={}
        )


@app.route("/elo", methods=['GET'])
def elo_get():
    try:
        team_id = request.args.get('team_id', type=int)
        match_datetime = parser.parse(request.args.get('datetime', type=str))
    except ValueError as e:
        return jsonify(
            isError=True,
            message=str(e),
            statusCode=400,
            data={}
        )
    # except TypeError as e:
    #     return jsonify(
    #         isError=True,
    #         message=str(e),
    #         statusCode=400,
    #         data={}
    #     )

    team_elo = elo.get_elo(team_id=team_id, match_datetime=match_datetime)
    return jsonify(
        isError=False,
        message="Success",
        statusCode=200,
        data={"team_id": team_id, "elo": team_elo}
    )


@app.route("/probability", methods=['GET'])
def probability_get():
    team_a_id = request.args.get('team_a', type=int)
    team_b_id = request.args.get('team_b', type=int)
    match_datetime = parser.parse(request.args.get('match_datetime', type=str))

    data = elo.calc_match_probability(team_a_id=team_a_id, team_b_id=team_b_id, match_datetime=match_datetime)
    return jsonify(
        isError=False,
        message="Success",
        statusCode=200,
        data=data
    )



