import json
import requests as req
from background_task import background

@background(schedule=30)
def runEvent(server_ip,server_id,event_type):
    payload = {'instance_id':server_id, 'secret_key':'m0nKEY'}
    successful_stoppage = []
    successful_count = 0

    unsuccessful_stoppage = []
    unsuccessful_count = 0

    results = {}

    if event_type == 'stop':
        server_url = 'http://' + server_ip + ":8999/ec2/instance/event/stop/"
    elif event_type == 'ddos':
        pass

    server_response = req.get(server_url, params=payload)
    server_jsonObj = json.loads(server_response.content.decode())

    if server_jsonObj['HTTPStatusCode'] == 200:
        successful_stoppage.append(server_id)
        successful_count += 1
    else:
        unsuccessful_stoppage.append(server_id)
        unsuccessful_count += 1

    results = {
        'successful':{
            'ids':successful_stoppage,
            'count':successful_count
        },
        'unsuccessful':{
            'ids':unsuccessful_stoppage,
            'count':unsuccessful_count
        }
    }

    return results
