from src.utils import *
from src.settings import configs
from src.football_events import FootballEvents


### logging ------------------------------------------------------------------------------

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

#------------------ dictionaries ----------------------------------------------------------
guides = {
    'map_competitor':'competitor',
    'map_method':'method',
    'map_action':'type',
    'map_breaks':'break_name',
    'map_period':'period_name',
}

if __name__ == "__main__":

    fe = FootballEvents()
    #-----------------------------------------
    for table_name, name_in_class in guides.items():
        if db.update_values(pd.DataFrame(fe.maps[name_in_class].items(), columns = ['value','id']),\
                            f"{configs['PG__SCHEMA']}.{table_name}",'id'):
            None
        else:
            log(logger, 'problem with updating maps', 'error', f"{configs['PG__SCHEMA']}.{table_name}")