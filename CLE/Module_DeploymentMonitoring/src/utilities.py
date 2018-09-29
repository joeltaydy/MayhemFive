import boto3
from Module_DeploymentMonitoring.src import aws_config
from Module_DeploymentMonitoring.models import *

def getAllImages(account_number,access_key,secret_access_key):
    images = {}

    client = boto3.client('ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=aws_config.REGION
    )
    results = client.describe_images(
        Owners=[
            account_number,
        ],
    )

    for image in results['Images']:
        images.update(
            {
                image['ImageId']:image['Name']
            }
        )

    return images

def createAccount(accountNum, class_studentObj):
    try:
        awsC=AWS_Credentials.objects.get(account_number=accountNum)
    except:
        awsC = AWS_Credentials.objects.create(
            account_number=accountNum,
        )
        awsC.save()
    class_studentObj.awscredential = awsC
    class_studentObj.save()
