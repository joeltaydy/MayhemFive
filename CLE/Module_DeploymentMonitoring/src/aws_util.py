import boto3
from aws_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION

#-----------------------------------------------------------------------------#
#-------------------------- Monitoring Functions -----------------------------#
#-----------------------------------------------------------------------------#

client = boto3.client('cloudwatch')
response = client.get_metric_data(DashboardName=)
