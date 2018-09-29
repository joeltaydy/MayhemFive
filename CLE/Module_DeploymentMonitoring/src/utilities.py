import boto3
import Module_DeploymentMonitoring.src import aws_config

def getAllTeamDetails():
    section_list = {}

    esm_course_sectionList = requests.session['courseList_update']['ESM201']
    for course_section in esm_course_sectionList:
        section_number = course_section['section_number']
        section_list[section_number] = {}

        query = Class.objects.filter(course_section=course_section['id']).values('team_number','awscredential').annotate(dcount=Count('team_number'))
        for team_details in query:
            team_name = team_details['team_number']
            account_number = team_details['awscredential']
            section_list[section_number].update(
                {
                    account_number:team_name
                }
            )

    return section_list

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
