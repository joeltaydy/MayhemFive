import json
import boto3
import requests as req
from background_task import background
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring.src import aws_util
from Module_TeamManagement.src.utilities import encode,decode
from Module_EventConfig.src import utilities

@background(schedule=0)
def test_tasks(message):
    print(message)


@background(schedule=0)
def stopServer(server_list=None,server=None):
    print('--- Running background event: Stop Server ---')

    # If stopping only a server
    if server !=  None:
        server_ip = server['server_ip']
        server_id = server['server_id']

        server_url = 'http://' + server_ip + ":8999/ec2/instance/event/stop/"
        payload = {'instance_id':server_id, 'secret_key':'m0nKEY'}
        server_response = req.get(server_url, params=payload)
        server_jsonObj = json.loads(server_response.content.decode())

        if server_jsonObj['HTTPStatusCode'] == 200:
            print('Successfully stopped server: ' + server_ip)
            utilities.writeEventLog("stop", server_ip )
        else:
            print('Unsuccessfully stopped server: ' + server_ip + '\n' + server_jsonObj)

    # If stopping multiple servers
    if server_list != None:
        for server in server_list:
            credentialsObj = AWS_Credentials.objects.get(account_number=server['server_account'])
            access_key = decode(credentialsObj.access_key)
            secret_access_key = decode(credentialsObj.secret_access_key)

            results = aws_util.stopServer(server['server_id'],access_key,secret_access_key)

            if results['StoppingInstances'][0]['CurrentState']['Code'] == 64:
                print('Successfully stopped server: ' + server['server_ip'])
                utilities.writeEventLog("stop", server['server_ip'] )
            else:
                print('Unsuccessfully stopped server: ' + server['server_ip'])

    print('--- Ending background event: Stop Server ---')


@background(schedule=0)
def dosAttack(server_list=None,server=None):
    print('--- Running background task: DDOS Attack ---')

    # If sending to one server
    if server !=  None:
        pass

    # If sending to  multiple servers
    if server_list != None:
        pass

    print('--- Ending background event: DDOS Attack ---')
