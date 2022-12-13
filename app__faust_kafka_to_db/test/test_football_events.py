import pytest
import sys
sys.path.append('../')
import re
import pandas as pd
from app__faust_kafka_to_db.src.football_events import FootballEvents


@pytest.fixture
def meta_instance():
    return {
        'id': 'sr:sport_event:27751076',
        'start_time': '2022-08-05T19:00:00+00:00',
        'sport_event_context_competition': {'id': 'sr:competition:17', 'name': 'Premier League', 'gender': 'men'},}


@pytest.fixture
def need_columns():
    return [
        'id', 'type', 'time', 'period', 'period_name', 'match_time', 'match_clock', 'competitor', 'outcome', 'home_score',
        'away_score', 'method', 'stoppage_time', 'stoppage_time_clock','injury_time_announced', 'break_name', 'event_id', 'score'
    ]


@pytest.fixture
def main_instance():
    return [
            {'id': 1225821747,
             'type': 'period_start',
             'time': '2022-08-06T14:00:15+00:00',
             'period': 1,
             'period_name': 'regular_period'},
            {'id': 1225822043,
             'type': 'throw_in',
             'time': '2022-08-06T14:00:25+00:00',
             'match_time': 1,
             'match_clock': '0:10',
             'competitor': 'home',
             'period': 1},
            {'id': 1225824079,
             'type': 'shot_off_target',
             'time': '2022-08-06T14:02:30+00:00',
             'match_time': 3,
             'match_clock': '2:15',
             'competitor': 'away',
             'period': 1,
             'outcome': 'miss'},
            {'id': 1225832259,
             'type': 'score_change',
             'time': '2022-08-06T14:11:48+00:00',
             'match_time': 12,
             'match_clock': '11:22',
             'competitor': 'away',
             'period': 1,
             'home_score': 0,
             'away_score': 1},
            {'id': 1225859309,
            'type': 'injury_time_shown',
            'time': '2022-08-06T14:45:37+00:00',
            'match_time': 45,
            'match_clock': '45:00',
            'stoppage_time': 1,
            'stoppage_time_clock': '0:22',
            'period': 1,
            'injury_time_announced': 2},
            {'id': 1225861213,
            'type': 'break_start',
            'time': '2022-08-06T14:48:01+00:00',
            'break_name': 'pause'},
            {'id': 1225887093,
            'type': 'score_change',
            'time': '2022-08-06T15:18:37+00:00',
            'match_time': 61,
            'match_clock': '60:04',
            'competitor': 'home',
            'period': 2,
            'home_score': 3,
            'away_score': 1,
            'method': 'own_goal'},
        ]

#------------------------------------------------------------------------------------------------------------------

def test__apply_meta_preprocessing(meta_instance):
    
    fet = FootballEvents(pd.DataFrame(), pd.json_normalize(meta_instance, sep = '_'))

    assert fet.meta_instance is True
    assert fet.data != {}
    assert 'event_id' in fet.data.keys()
    assert fet.data['competitions_matches'].shape[0] > 0
    assert fet.data['competitions'].shape[0] > 0


def test__apply_main_preprocessing(main_instance, meta_instance, need_columns):
    
    fet = FootballEvents(pd.DataFrame(main_instance), pd.json_normalize(meta_instance, sep = '_'))

    assert all([fet.meta_instance, fet.main_instance]) is True
    assert fet.data != {}
    assert fet.df_main.shape[0] > 0
    assert set(list(fet.df_main)) & set(need_columns) == set(need_columns)


def test_match_actions(main_instance, meta_instance):
    
    fet = FootballEvents(pd.DataFrame(main_instance), pd.json_normalize(meta_instance, sep = '_'))
    load = fet.match_actions()

    assert all([fet.meta_instance, fet.main_instance]) is True
    assert load is True
    assert fet.data['match_actions'].shape[0] > 0
    assert isinstance(fet.data['match_actions']['match_clock'].values[0], list)
    assert type(fet.data['match_actions']['match_clock'].values[0][0]) == int


def test_match_missed_goals(main_instance, meta_instance):
    
    fet = FootballEvents(pd.DataFrame(main_instance), pd.json_normalize(meta_instance, sep = '_'))
    load = fet.match_missed_goals()

    assert all([fet.meta_instance, fet.main_instance]) is True
    assert load is True
    assert fet.data['match_missed_goals'].shape[0] > 0
    assert isinstance(fet.data['match_missed_goals']['score'].values[0], list)
    assert type(fet.data['match_missed_goals']['score'].values[0][0]) == int
    assert isinstance(fet.data['match_missed_goals']['match_time'].values[0], float)


def test_match_goals(main_instance, meta_instance):
    
    fet = FootballEvents(pd.DataFrame(main_instance), pd.json_normalize(meta_instance, sep = '_'))
    load = fet.match_goals()

    assert all([fet.meta_instance, fet.main_instance]) is True
    assert load is True
    assert fet.data['match_goals'].shape[0] > 0
    assert isinstance(fet.data['match_goals']['score'].values[0], list)
    assert fet.data['match_goals'].loc[fet.data['match_goals']['map_method'].isnull()].empty


def test_match_breaks(main_instance, meta_instance):
    
    fet = FootballEvents(pd.DataFrame(main_instance), pd.json_normalize(meta_instance, sep = '_'))
    load = fet.match_breaks()

    assert all([fet.meta_instance, fet.main_instance]) is True
    assert load is True
    assert fet.data['match_breaks'].shape[0] > 0
    assert isinstance(fet.data['match_breaks']['stoppage_time_clock'].values[0], list)
    assert isinstance(fet.data['match_breaks']['stoppage_time'].values[0], float)