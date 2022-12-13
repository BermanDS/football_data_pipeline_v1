from src.streamapi import *
from src.settings import configs

##################### init Kafka connector ----------------------------------------------

db_broker = DBkafka(
    topic = configs['KAFKA__TOPIC'],
    log_path = configs['LOG__PATH'],
    headers = {'version':'1.1'},
    tz = configs['timezone'],
    host = configs['KAFKA__HOST'], 
    port = configs['KAFKA__PORT'],
    value_serializer = lambda x: json.dumps(x).encode('utf-8'),
)

#################### init Stream processing instance ---------------------------------------

apistream = streamAPI(
    url = f"http://{configs['STREAMING__HOST']}:{configs['PORT']}/streaming_example",
    log_path = configs['LOG__PATH'],
    db_broker = db_broker,
)

###############################################################################################

if __name__ == "__main__":
    
    apistream.start_streaming()