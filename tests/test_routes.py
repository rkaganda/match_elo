import urllib.request, json, urllib.parse
import datetime
import random
import pytest


def generate_random_match():
    teams = [s for s in range(0, 20)]
    match_datetime = datetime.datetime.now() - (random.random() * datetime.timedelta(days=1))
    random.shuffle(teams)
    match = {
        'match_id': random.randint(0, 1000),
        'match_datetime': match_datetime,
        'winning_team': teams[0],
        'losing_team': teams[-1],
        'update_elo': True
    }

    return match


@pytest.fixture
def single_match():
    pytest.single_match = {
        'match_id': -100,
        'match_datetime': datetime.datetime.now(),
        'winning_team': -1,
        'losing_team': -2,
        'update_elo': True
    }


def test_post_match(single_match):
    url = 'http://127.0.0.1:5000/match'

    data = urllib.parse.urlencode(pytest.single_match).encode()
    req = urllib.request.Request(
        url,
        data=data,
    )
    with urllib.request.urlopen(req) as url:
        response = json.loads(url.read().decode())
        print(response)
        assert (response['statusCode'] == 201 and response['data']['match_id'] == pytest.single_match['match_id'])


def test_match_get(single_match):
    data = urllib.parse.urlencode({
        'match_id': pytest.single_match['match_id']
    })
    full_url = "http://127.0.0.1:5000/match?{}".format(data)
    req = urllib.request.Request(
        full_url,
        data=None,
    )
    with urllib.request.urlopen(req) as url:
        response = json.loads(url.read().decode())
        print(response)
        assert (response['statusCode'] == 200 and response['data']['match_id'] == pytest.single_match['match_id'])


def test_elo_get(single_match):
    data = urllib.parse.urlencode({
        'team_id': pytest.single_match['winning_team'],
        'datetime': pytest.single_match['match_datetime'] + datetime.timedelta(days=1)
    })
    full_url = "http://127.0.0.1:5000/elo?{}".format(data)
    req = urllib.request.Request(
        full_url,
    )
    with urllib.request.urlopen(req) as url:
        response = json.loads(url.read().decode())
        print(response)
        assert (response['statusCode'] == 200)


def test_probability_get():
    data = urllib.parse.urlencode({
        'team_a': pytest.single_match['winning_team'],
        'team_b': pytest.single_match['losing_team'],
        'match_datetime': pytest.single_match['match_datetime'] + datetime.timedelta(days=1)
    })
    full_url = "http://127.0.0.1:5000/probability?{}".format(data)
    req = urllib.request.Request(
        full_url,
        data=None,
    )
    with urllib.request.urlopen(req) as url:
        response = json.loads(url.read().decode())
        print(response)
        assert (response['statusCode'] == 200)


def test_match_delete(single_match):
    url = 'http://127.0.0.1:5000/match'

    data = urllib.parse.urlencode(pytest.single_match)
    full_url = "http://127.0.0.1:5000/match?{}".format(data)
    req = urllib.request.Request(
        full_url,
        data=None,
        method='DELETE'
    )
    with urllib.request.urlopen(req) as url:
        response = json.loads(url.read().decode())
        print(response)
        assert (response['statusCode'] == 204)
