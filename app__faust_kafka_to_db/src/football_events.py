"""Football events processing module."""
import re
import os
import json
import pandas as pd

class FootballEvents:
    """Class that splite a football match to separate instances."""

    def __init__(self,
                df_main: object  = pd.DataFrame(), 
                df_meta: object = pd.DataFrame()):
        """
        :df_main: Main instance of data.
        :df_meta: Meta data about competition
        """

        self.df_main = df_main
        self.df_meta = df_meta
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
        }
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
        }
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
        }
        self.global_score = [0,0]
        self.main_instance = False
        self.meta_instance = False
        self._apply_meta_preprocessing()
        self._apply_main_preprocessing()


    def udf_score(self, x: object) -> list:
        """
        processing score from two atributes home_score and away_score
        to presentation [0, 1] where first element is home_score, second element is away_score
        """

        if x['home_score'] + x['away_score'] >= 0:
            self.global_score[0] = x['home_score']
            self.global_score[1] = x['away_score']

        return self.global_score.copy()
        
    
    def _apply_main_preprocessing(self):
        """
        Apply preprocessing the main instance of data with key 'timeline' 
        there are have to need three atribures 'home_score','away_score','match_clock', if some of them is absence --> False
        the atribute stoppage_time_clock not necessary strongly --> True
        """

        if set(['home_score','away_score','match_clock']) & set(list(self.df_main)) == set(['home_score','away_score','match_clock']) and \
            not self.df_main.empty and \
            self.meta_instance:
            #------------------------------------------------------------------------------------------------------
            self.df_main['score'] = self.df_main.fillna(self.fillna_values)\
                                                .astype({'away_score':int, 'home_score':int})\
                                                .apply(lambda x: self.udf_score(x), axis = 1)
            self.df_main['match_clock'] = self.df_main.fillna(self.fillna_values)['match_clock']\
                                                      .apply(lambda x: list(map(int, x.split(':'))))
            #-----------------------------------------------------------------------------------------------------
            if 'stoppage_time_clock' in list(self.df_main):
                self.df_main['stoppage_time_clock'] = self.df_main.fillna(self.fillna_values)['stoppage_time_clock']\
                                                          .apply(lambda x: list(map(int, x.split(':'))))
            else:
                self.df_main['stoppage_time_clock'] = [list(map(int, self.fillna_values['stoppage_time_clock'].split(':')))]
            #------------------------------------------------------------------------------------------------------
            self.df_main['event_id'] = self.data['event_id']
            self.main_instance = True


    def _apply_meta_preprocessing(self):
        """
        Apply preprocessing the additional metainfo instance of data with key 'sprt_event' 
        there are have to need two atribures 'id','start_time', if some of them is absence --> False
        the atributes : competition_id, competition_name and competition_gender not necessary strongly --> True
        """

        if set(['id','start_time']) & set(list(self.df_meta)) == set(['id','start_time']) and not self.df_meta.empty:
            if 'sport_event_context_competition_id' not in list(self.df_meta): self.df_meta['sport_event_context_competition_id'] = -1
            #-----------------cleansing id values ------------------------------------------------------------------
            for col_ in ['id','sport_event_context_competition_id']:
                self.df_meta[col_] = self.df_meta[col_].apply(lambda x: re.sub(r'\D','',x))
            #------------------------------------------------------------------------------------------------------
            self.data['competitions_matches'] = self.df_meta.astype({'id':'int64','sport_event_context_competition_id':'int32'})\
                                                            .rename({'id':'event_id','sport_event_context_competition_id':'competition_id'}, axis = 1)\
                                                            [['event_id','start_time','competition_id']]
            self.data['event_id'] = self.df_meta['id'].values[0]
            #------------------------------------------------------------------------------------------------------
            self.meta_instance = True
        #-###############################################################################################################
        if set(['sport_event_context_competition_id', 'sport_event_context_competition_name', 'sport_event_context_competition_gender']) &\
            set(list(self.df_meta)) ==\
            set(['sport_event_context_competition_id', 'sport_event_context_competition_name', 'sport_event_context_competition_gender']) and \
            not self.df_meta.empty:
            #-----------------------------------------------------------------------------------------------------
            self.data['competitions'] = self.df_meta.astype({'sport_event_context_competition_id':'int32'})\
                                                    .rename({'sport_event_context_competition_name':'competition_name',\
                                                             'sport_event_context_competition_id':'competition_id',\
                                                             'sport_event_context_competition_gender':'competition_gender'}, axis = 1)\
                                                            [['competition_id','competition_name','competition_gender']]
    

    def match_actions(self) -> bool:
        """
        Assemble main instance of all actions per match
        """

        if not all([self.main_instance, self.meta_instance]):
            return False
        else:
            self.data['match_actions'] = self.df_main.fillna(self.fillna_values)\
                                                     .replace({k:v for k,v in self.maps.items()})\
                                                     .rename({'period_name':'map_period','competitor':'map_competitor',\
                                                              'type':'map_action','time':'datetime'},axis = 1)\
                                                     .astype({'id':'int64','event_id':'int64','map_action':'int16','period':'int16',\
                                                              'map_period':'int16','map_competitor':'int16','match_time':'float'})\
                                                    [self.maininstances['match_actions']]
            return True
    

    def match_missed_goals(self) -> bool:
        """
        Assemble instance of missed goals per match
        """

        if not all([self.main_instance, self.meta_instance]) or 'outcome' not in list(self.df_main):
            return False
        else:
            self.data['match_missed_goals'] = \
                self.df_main.fillna(self.fillna_values)\
                            .loc[~self.df_main['outcome'].isnull()]\
                            .replace({k:v for k,v in self.maps.items()})\
                            .rename({'competitor':'map_competitor','type':'map_action','time':'datetime'},axis = 1)\
                            .astype({'id':'int64','event_id':'int64','map_action':'int16','period':'int16',\
                                     'map_competitor':'int16','match_time':'float'})\
                            [self.maininstances['match_missed_goals']]
            
            return not self.data['match_missed_goals'].empty
    

    def match_goals(self) -> bool:
        """
        Assemble actions of goals per match
        """

        if not all([self.main_instance, self.meta_instance]):
            return False
        else:
            if 'method' not in list(self.df_main): self.df_main['method'] = None
            #----------------------------------------------------------------------
            self.data['match_goals'] = \
                self.df_main.loc[(~self.df_main['method'].isnull())|\
                                 (self.df_main['type'].str.startswith('score'))]\
                            .fillna(self.fillna_values)\
                            .replace({k:v for k,v in self.maps.items()})\
                            .rename({'competitor':'map_competitor','type':'map_action','time':'datetime',\
                                     'method':'map_method'},axis = 1)\
                            .astype({'id':'int64','event_id':'int64','map_action':'int16','period':'int16',
                                     'map_competitor':'int16','match_time':'float','map_method':'int16'})\
                            [self.maininstances['match_goals']]
            
            return not self.data['match_goals'].empty
    

    def match_breaks(self) -> bool:
        """
        Assemble breaks per match
        """

        if not all([self.main_instance, self.meta_instance]):
            return False
        else:
            if 'stoppage_time' not in list(self.df_main): self.df_main['stoppage_time'] = None
            if 'break_name' not in list(self.df_main): self.df_main['break_name'] = None
            #----------------------------------------------------------------------
            self.data['match_breaks'] = \
                self.df_main.loc[(~self.df_main['stoppage_time'].isnull())|\
                                 (~self.df_main['break_name'].isnull())]\
                            .fillna(self.fillna_values)\
                            .replace({k:v for k,v in self.maps.items()})\
                            .rename({'period_name':'map_period','competitor':'map_competitor','type':'map_action',\
                                     'break_name':'map_breaks','time':'datetime'},axis = 1)\
                            .astype({'id':'int64','event_id':'int64','map_action':'int16','map_period':'int16',
                                     'map_breaks':'int16','match_time':'float'})\
                            [self.maininstances['match_breaks']]
            
            return not self.data['match_breaks'].empty
