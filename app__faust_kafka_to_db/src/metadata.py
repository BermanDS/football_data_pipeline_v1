"""Football events processing module."""
import re
import os
import json
import pandas as pd


class MetaDataEvents:
    """
    Class that define maps and other meta data for processing data
    """

    def __init__(self, 
                guides: dict = {},
                maps_instances: dict = {},
                fillna_values: dict = {},
                maininstances_features: dict = {}):
        """
        :maps_instances - values for main instances as normalization
        :fillna values - dictinary of filling Nan values
        :maininstances_features - the guide of set attributes for clean data layer
        :guides - mapping attributes between raw and clean data
        """
        
        self.data = {}
        self.maps = {
            'type': {
                'match_started':1, 
                'free_kick':2,  
                'throw_in':3, 
                'goal_kick':4, 
                'corner_kick':5, 
                'shot_off_target':6, 
                'substitution':7, 
                'shot_on_target':8, 
                'shot_saved':9, 
                'possible_goal':10, 
                'score_change':11, 
                'yellow_card':12, 
                'period_start':0, 
                'injury_time_shown':13,
                'injury_return':14, 
                'injury':15, 
                'offside':16,  
                'period_score':17, 
                'break_start':18, 
                'match_ended':19, 
                'unknown':-1,
                'video_assistant_referee':20,
                'video_assistant_referee_over':21,
                'penalty_awarded':22,
            },
            'period_name':{
                'regular_period':1,
            },
            'competitor':{
                'home':1, 
                'away':2,
                'blank':0,
            },
            'break_name':{
                'pause':1,
                'stop':2,
                'blank':0,
            },
            'method':{
                'header':2, 
                'own_goal':3, 
                'foot':1,
                'penalty':4,
            },
        } if maps_instances == {} else maps_instances
        self.fillna_values = {
            'period_name':'regular_period', 
            'type':'unknown',
            'period':0,
            'match_time':0,
            'competitor':'blank',
            'match_clock':'-1:00',
            'method':'foot',
            'home_score':-1,
            'away_score':-1,
            'stoppage_time_clock':'-1:00',
            'injury_time_announced':0,
            'break_name':'stop',
            'stoppage_time':0,
        } if fillna_values == {} else fillna_values
        self.maininstances = {
            'match_actions': [
                'id','event_id', 'map_action', 'datetime', 'period', 'map_period', 'match_time','match_clock','map_competitor','score'],
            'match_missed_goals': [
                'id','event_id','map_action','datetime','period','score','match_time','match_clock','map_competitor'],
            'match_goals': [
                'id','event_id','map_action','datetime','period','score','match_time','match_clock','map_competitor','map_method'],
            'match_breaks': [
                'id','event_id','map_action','datetime','score','map_period','match_time','stoppage_time','stoppage_time_clock',
                'injury_time_announced','map_breaks'],
        } if maininstances_features == {} else maininstances_features
        self.guides = {
            'map_competitor':'competitor',
            'map_method':'method',
            'map_action':'type',
            'map_breaks':'break_name',
            'map_period':'period_name',
        } if guides == {} else guides
        self.required_features = {
            'meta_instance':['sport_event_context_competition_id', 'sport_event_context_competition_name', 'sport_event_context_competition_gender'],
            'main_instance':['home_score','away_score','match_clock'],
        }
        self.global_score = [0,0]
        self.main_instance = False
        self.meta_instance = False
        

    def udf_score(self, x: object) -> list:
        """
        processing score from two atributes home_score and away_score
        to presentation [0, 1] where first element is home_score, second element is away_score
        """

        if x['home_score'] + x['away_score'] >= 0:
            self.global_score[0] = x['home_score']
            self.global_score[1] = x['away_score']

        return self.global_score.copy()