"""Football events processing module."""
from .metadata import *


class FootballEvents(MetaDataEvents):
    """
    Class that splite a football match to separate instances.
    """

    def __init__(self,
                df_main: object = pd.DataFrame(), 
                df_meta: object = pd.DataFrame()):
        """
        :df_main: Main instance of data.
        :df_meta: Meta data about competition
        """
        
        MetaDataEvents.__init__(self)
        
        self.df_main = df_main
        self.df_meta = df_meta
        self._apply_meta_preprocessing()
        self._apply_main_preprocessing()
    
    
    def _apply_main_preprocessing(self):
        """
        Apply preprocessing the main instance of data with key 'timeline' 
        there are have to need three atribures 'home_score','away_score','match_clock', if some of them is absence --> False
        the atribute stoppage_time_clock not necessary strongly --> True
        """

        if set(self.required_features['main_instance']) & set(list(self.df_main)) == \
            set(self.required_features['main_instance']) and \
            not self.df_main.empty and \
            self.meta_instance:
            #-----------------------------------------------------------------
            self.df_main['score'] = (
                self.df_main.fillna(self.fillna_values)
                .astype({'away_score':int, 'home_score':int})
                .apply(lambda x: self.udf_score(x), axis = 1)
            )
            self.df_main['match_clock'] = (
                self.df_main.fillna(self.fillna_values)['match_clock']
                .apply(lambda x: list(map(int, x.split(':'))))
            )
            #---------------------------------------------------------------------------
            if 'stoppage_time_clock' in list(self.df_main):
                self.df_main['stoppage_time_clock'] = (
                    self.df_main.fillna(self.fillna_values)['stoppage_time_clock']
                    .apply(lambda x: list(map(int, x.split(':'))))
                )
            else:
                self.df_main['stoppage_time_clock'] = \
                    [list(map(int, self.fillna_values['stoppage_time_clock'].split(':')))]
            #---------------------------------------------------------------------------
            self.df_main['event_id'] = self.data['event_id']
            self.main_instance = True


    def _apply_meta_preprocessing(self):
        """
        Apply preprocessing the additional metainfo instance of data with key 'sprt_event' 
        there are have to need two atribures 'id','start_time', if some of them is absence --> False
        the atributes : competition_id, competition_name and competition_gender not necessary strongly --> True
        """

        if set(['id','start_time']) & set(list(self.df_meta)) == set(['id','start_time']) and \
            not self.df_meta.empty:
            if 'sport_event_context_competition_id' not in list(self.df_meta): 
                self.df_meta['sport_event_context_competition_id'] = -1
            #-----------------cleansing id values ---------------------------
            for col_ in ['id','sport_event_context_competition_id']:
                self.df_meta[col_] = self.df_meta[col_].apply(lambda x: re.sub(r'\D','',x))
            #----------------------------------------------------------------
            self.data['competitions_matches'] = (
                self.df_meta.astype({'id':'int64','sport_event_context_competition_id':'int32'})
                .rename({'id':'event_id','sport_event_context_competition_id':'competition_id'}, axis = 1)
                [['event_id','start_time','competition_id']]
            )                                       
            self.data['event_id'] = self.df_meta['id'].values[0]
            #-----------------------------------------------------------------
            self.meta_instance = True
        #-####################################################################
        if set(self.required_features['meta_instance']) & set(list(self.df_meta)) == \
            set(self.required_features['meta_instance']) and \
            not self.df_meta.empty:
            #-----------------------------------------------------------------
            self.data['competitions'] = (
                self.df_meta.astype({'sport_event_context_competition_id':'int32'})
                .rename({'sport_event_context_competition_name':'competition_name',\
                         'sport_event_context_competition_id':'competition_id',\
                         'sport_event_context_competition_gender':'competition_gender'}, axis = 1)
                [['competition_id','competition_name','competition_gender']]
            )
    

    def match_actions(self) -> bool:
        """
        Assemble main instance of all actions per match
        """

        if not all([self.main_instance, self.meta_instance]):
            return False
        else:
            self.data['match_actions'] = (
                self.df_main.fillna(self.fillna_values)
                .replace({k:v for k,v in self.maps.items()})
                .rename({'period_name':'map_period','competitor':'map_competitor',\
                         'type':'map_action','time':'datetime'}, axis = 1)
                .astype({'id':'int64','event_id':'int64','map_action':'int16','period':'int16',\
                         'map_period':'int16','map_competitor':'int16','match_time':'float'})
                [self.maininstances['match_actions']]
            )
            return True
    

    def match_missed_goals(self) -> bool:
        """
        Assemble instance of missed goals per match
        """

        if not all([self.main_instance, self.meta_instance]) or 'outcome' not in list(self.df_main):
            return False
        else:
            self.data['match_missed_goals'] = (
                self.df_main.fillna(self.fillna_values)
                .loc[~self.df_main['outcome'].isnull()]
                .replace({k:v for k,v in self.maps.items()})
                .rename({'competitor':'map_competitor','type':'map_action','time':'datetime'},axis = 1)
                .astype({'id':'int64','event_id':'int64','map_action':'int16',\
                         'period':'int16','map_competitor':'int16','match_time':'float'})
                [self.maininstances['match_missed_goals']]
            )            
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
            self.data['match_goals'] = (
                self.df_main.loc[(~self.df_main['method'].isnull())|(self.df_main['type'].str.startswith('score'))]
                .fillna(self.fillna_values)
                .replace({k:v for k,v in self.maps.items()})
                .rename({'competitor':'map_competitor','type':'map_action','time':'datetime',\
                         'method':'map_method'}, axis = 1)
                .astype({'id':'int64','event_id':'int64','map_action':'int16','period':'int16',
                         'map_competitor':'int16','match_time':'float','map_method':'int16'})
                [self.maininstances['match_goals']]
            )            
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
            self.data['match_breaks'] = (
                self.df_main.loc[(~self.df_main['stoppage_time'].isnull())|(~self.df_main['break_name'].isnull())]
                .fillna(self.fillna_values)
                .replace({k:v for k,v in self.maps.items()})
                .rename({'period_name':'map_period','competitor':'map_competitor','type':'map_action',\
                         'break_name':'map_breaks','time':'datetime'}, axis = 1)
                .astype({'id':'int64','event_id':'int64','map_action':'int16','map_period':'int16',\
                         'map_breaks':'int16','match_time':'float'})
                [self.maininstances['match_breaks']]
            )            
            return not self.data['match_breaks'].empty