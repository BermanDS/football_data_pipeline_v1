import faust
from .src.utils import *
from .src.settings import configs
from .src.football_events import FootballEvents


## logging

logger = logger_init(location = 'faust_apps', log_path = f"./{configs['LOG__PATH']}")

### DB instance ----------------------------------------------------------------------------

db = DBpostgreSQL(
    db_name = configs['PG__DBNAME'],
    host = configs['PG__HOST'],
    username = configs['PG__USER_BOT'],
    password= configs['PG__PASSW_BOT'], 
    tz = configs['timezone'], 
)
db.logger = logger

#### Main app initializing ----------------------------------------------------------------
app = faust.App(
    'info_football_events',
    broker=f"kafka://{configs['KAFKA__HOST']}:{configs['KAFKA__PORT']}",
    value_deserializer=lambda x: x.decode(),
)
#### Kafka topic definition ---------------------------------------------------------------

kafka_topic = app.topic(configs['KAFKA__TOPIC'], value_type=bytes)

#### defining Faust agent for processing ---------------------------------------------------

@app.agent(kafka_topic)
async def process(transactions):
    async for value in transactions:
        
        if not isinstance(value, dict): value = json.loads(value)
        ############## Processing and saving to DB -----------------------------------------
        if set(value.keys()) & set(['sport_event', 'timeline']) != set(['sport_event', 'timeline']):
            log(logger, 'absence the some of dependecies', 'error', str(value.keys()))
            continue
        #----------------------------------------------------------------------------------
        try:
            fe = FootballEvents(pd.DataFrame(value['timeline']), pd.json_normalize(value['sport_event'], sep = '_'))
        except Exception as err:
            log(logger, 'parser is broken or new version of data', 'error', str(err))
            continue
        #----------------------------------------------------------------------------------
        if not all([fe.main_instance, fe.meta_instance]):
            log(logger, 'some of instances not parsed', 'error', f"main is {fe.main_instance}, meta is {fe.meta_instance}")
            continue
        #-----------------------------------------------------------------------------------
        if 'competitions' in fe.data.keys():
            if db.update_values(fe.data['competitions'], f"{configs['PG__SCHEMA']}.competitions",'competition_id'):
                None
            else:
                log(logger, 'problem with saving data', 'error', "competitions")
        else:
            log(logger, 'there are not data', 'error', "competitions")
        #----------------------------------------------------------------------------------
        if fe.meta_instance:
            if db.update_values(fe.data['competitions_matches'], f"{configs['PG__SCHEMA']}.competitions_matches", 'event_id'):
                None
            else:
                log(logger, 'problem with saving data', 'error', f"competitions_matches for event {fe.data['event_id']}")
        else:
            log(logger, 'there are not data', 'error', "competitions_matches")
        #------------------------------------------------------------------------------------
        if fe.match_actions():
            if db.update_values(fe.data['match_actions'], f"{configs['PG__SCHEMA']}.match_actions", 'event_id,id'):
                None
            else:
                log(logger, 'problem with saving data', 'error', f"match_actions for event {fe.data['event_id']}")
        else:
            log(logger, 'problem with parsing data', 'error', "match_actions")
        #-----------------------------------------------------------------------------------
        if fe.match_missed_goals():
            if db.update_values(fe.data['match_missed_goals'], f"{configs['PG__SCHEMA']}.match_missed_goals", 'event_id,id'):
                None
            else:
                log(logger, 'problem with saving data', 'error', f"match_missed_goals for event {fe.data['event_id']}")
        else:
            log(logger, 'there are not data', 'error', "match_missed_goals")
        #-----------------------------------------------------------------------------------
        if fe.match_goals():
            if db.update_values(fe.data['match_goals'], f"{configs['PG__SCHEMA']}.match_goals", 'event_id,id'):
                None
            else:
                log(logger, 'problem with saving data', 'error', f"match_goals for event {fe.data['event_id']}")
        else:
            log(logger, 'there are not data', 'error', "match_goals")
        #-----------------------------------------------------------------------------------
        if fe.match_breaks():
            if db.update_values(fe.data['match_breaks'], f"{configs['PG__SCHEMA']}.match_breaks", 'event_id,id'):
                None
            else:
                log(logger, 'problem with saving data', 'error', f"match_breaks for event {fe.data['event_id']}")
        else:
            log(logger, 'there are not data', 'error', "match_breaks")
        #-----------------------------------------------------------------------------------
        fe.data.clear()
        gc.collect()
        ########################################################################################