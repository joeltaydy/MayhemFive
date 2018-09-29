import boto3
import Module_DeploymentMonitoring.src import aws_config

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
        images[image['ImageId']] = image['Name']

    return images
