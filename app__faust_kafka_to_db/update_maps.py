from src.utils import *
from src.settings import configs
from src.metadata import MetaDataEvents


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

if __name__ == "__main__":

    fe = MetaDataEvents()
    #-----------------------------------------
    for table_name, name_in_class in fe.guides.items():
        if db.update_values(pd.DataFrame(fe.maps[name_in_class].items(), columns = ['value','id']),\
                            f"{configs['PG__SCHEMA']}.{table_name}",'id'):
            None
        else:
            log(logger, 'problem with updating maps', 'error', f"{configs['PG__SCHEMA']}.{table_name}")