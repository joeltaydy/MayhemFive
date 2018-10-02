import boto3
from botocore.exceptions import ClientError
from Module_DeploymentMonitoring.src import config, server_util

# Get and connects to AWS SDK via boto3
def getClient(access_key,secret_access_key,region_name=None,service=None):
    if region_name == None:
        region_name = config.REGION_NAME

    if service == None:
        service = 'ec2'

    client = boto3.client(service,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

    return client


# Check if valid account number
def validateAccountNumber(account_number,access_key,secret_access_key):
    client = getClient(access_key,secret_access_key,service='sts')
    try:
        account = client.get_caller_identity()
    except ClientError as e:
        raise Exception("Invalid parameters. Please specify a valid access key and secret access key.")

    return account_number == account['Account']


# Return public key : String
# def generateKeyPair(username,access_key,secret_access_key):
#     try:
#         client = getClient(access_key,secret_access_key)
#         response = client.create_key_pair(KeyName=username)
#     except:
#         results = delAWSKeyPair(username)
#         if results['status']:
#             response = client.create_key_pair(KeyName=username)
#         else:
#             raise Exception(results['message'])
#
#     private_key = response['KeyMaterial']
#     key_name = response['KeyName']
#
#     return {'key_name':key_name,'private_key':private_key}


# Return True is successful delete. ELSE False
def deleteAWSKeyPair(username,access_key,secret_access_key):
    try:
        client = getClient(access_key,secret_access_key)
        response = client.delete_key_pair(KeyName=username)
    except Exception as e:
        return {'status':False,'message':e.args[0]}

    return {'status':True,'message':None}


# Get all images from user account via Boto3
def getAllImages(account_number,access_key,secret_access_key,client=None):
    images = {}

    if client == None:
        client = getClient(access_key,secret_access_key)

    try:
        results = client.describe_images(
            Owners=[
                account_number,
            ],
        )

        for image in results['Images']:
            images[image['ImageId']] = image['Name']
    except ClientError as e:
        raise Exception('Invalid Access_Key and Secret_Access_Key. Please key in a valid one')

    return images


# Add user to Image launch permission
def addUserToImage(image_id,account_number,access_key,secret_access_key,client=None):
    if client == None:
        client = getClient(access_key,secret_access_key)

    shared_response = client.modify_image_attribute(
        Attribute='launchPermission',
        ImageId=image_id,
        OperationType='add',
        UserIds=[
            account_number,
        ],
    )


# Remove user to Image launch permission
def removeUserFromImage(image_id,account_number,access_key,secret_access_key,client=None):
    if client == None:
        client = getClient(access_key,secret_access_key)

    shared_response = client.modify_image_attribute(
        Attribute='launchPermission',
        ImageId=image_id,
        OperationType='remove',
        UserIds=[
            account_number,
        ],
    )
