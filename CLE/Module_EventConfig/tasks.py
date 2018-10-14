import json
import boto3
import requests as req
from background_task import background
from Module_DeploymentMonitoring.models import *
from Module_DeploymentMonitoring.src import aws_util
from Module_TeamManagement.src.utilities import encode,decode


@background(schedule=0)
def test_tasks(message):
    print(message)


@background(schedule=0)
def stopServer(server_list=None,server=None):
    print('--- Running background event: Stop Server ---')

    # If stopping only a server
    if server !=  None:
        try:
            server_ip = server.IP_address
            server_url = 'http://' + server_ip + ":8999/ec2/instance/event/stop/"
            server_response = req.get(server_url, params=payload)
            server_jsonObj = json.loads(server_response.content.decode())

            if server_jsonObj['HTTPStatusCode'] == 200:
                print('Successfully stopped server: ' + server_ip)
            else:
                raise Exception('Unsuccessfully stopped server: ' + server_ip + '\n' + server_jsonObj)

        except Exception as e:
            raise e

    # If stopping multiple servers
    if server_list != None:
        try:
            for server in server_list:
                credentialsObj = AWS_Credentials.objects.get(account_number=server.account_number)
                access_key = decode(credentialsObj.access_key)
                secret_access_key = decode(credentialsObj.secret_access_key)

                results = aws_util.stopServer(server.instanceid,access_key,secret_access_key)

                if results['StoppingInstances'][0]['CurrentState']['Code'] == 64:
                    print('Successfully stopped server: ' + server.IP_address)
                else:
                    print('Unsuccessfully stopped server: ' + server_ip)

        except Exception as e:
            raise e

    print('--- Ending background event: Stop Server ---')


@background(schedule=0)
def ddosAttack(server_list=None,server=None):
    print('--- Running background task: DDOS Attack ---')
    print('--- Ending background event: DDOS Attack ---')
