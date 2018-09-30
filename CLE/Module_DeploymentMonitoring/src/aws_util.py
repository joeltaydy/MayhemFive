import boto3
from Module_DeploymentMonitoring.src import aws_config, server_util

# Get and connects to AWS SDK via boto3
def getEC2Client(access_key,secret_access_key,region_name=None):
    if region_name == None:
        region_name = aws_config.REGION

    client = boto3.client('ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

    return client


# Return public key : String
# def generateKeyPair(username,access_key,secret_access_key):
#     try:
#         client = getEC2Client(access_key,secret_access_key)
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
        client = getEC2Client(access_key,secret_access_key)
        response = client.delete_key_pair(KeyName=username)
    except Exception as e:
        return {'status':False,'message':e.args[0]}

    return {'status':True,'message':None}


# Get all images from user account via Boto3
def getAllImages(client=None,account_number,access_key,secret_access_key):
    images = {}

    if client == None:
        client = getEC2Client(access_key,secret_access_key)

    results = client.describe_images(
        Owners=[
            account_number,
        ],
    )

    for image in results['Images']:
        images[image['ImageId']] = image['Name']

    return images


# Add user to Image launch permission
def addUserToImage(client=None,image_id,account_number,access_key,secret_access_key):
    if client == None:
        client = getEC2Client(access_key,secret_access_key)

    shared_response = client.modify_image_attribute(
        Attribute='launchPermission',
        ImageId=image_id,
        OperationType='add',
        UserIds=[
            account_number,
        ],
    )


# Remove user to Image launch permission
def removeUserFromImage(client=None,image_id,account_number,access_key,secret_access_key):
    if client == None:
        client = getEC2Client(access_key,secret_access_key)

    shared_response = client.modify_image_attribute(
        Attribute='launchPermission',
        ImageId=image_id,
        OperationType='remove',
        UserIds=[
            account_number,
        ],
    )
