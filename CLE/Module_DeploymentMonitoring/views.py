import traceback
import requests as req
from django.shortcuts import render
from Module_DeploymentMonitoring.models import *

def run_UAT_Process(requests):
    response = {}

    action = request.GET.get('action')
    secret_key = 'm0nKEY'
    image_id = ''
    snapshot_id = ''

    try:
        if action == 'Launch':
            url_elastic_ip_retrieve = 'http://52.76.46.177:8999/ec2/elastic_ip/list/'
            url_instance_launch = 'http://52.76.46.177:8999/ec2/instance/event/launch/'
            payload = {'secret_key':secret_key, 'image_id':image_id, 'snapshot_id':snapshot_id}

            r_instance = requests.get(url_instance_launch, params=payload)
            response = r_instance.text

            for instance in response['instance_ids']:
                Instance.objects.create(
                    instance_id=instance.instance_id
                )

            r_ids = requests.get(url_elastic_ip_retrieve)
            response = r_ids.text

            for elastic_ips in response['Elastic_IPs']:
                for elastic_ip in elastic_ips['Unassigned']:
                    Elastic_IPs.objects.create(
                        allocation_id=elastic_ip.AllocationId
                    )

        elif action == 'Associate':
            pass
            url_elastic_ip_associate = 'http://52.76.46.177:8999/ec2/ec2/elastic_ip/associate/'
            payload = {'instance_id':secret_key, 'allocation_id':image_id,}
            r_ips = requests.get(url_elastic_ip_associate, params=payload)

            url_instance_stop = 'http://52.76.46.177:8999/ec2/instance/event/stop/'
            r_stop = requests.get(url_instance_stop)

            url_instance_start = 'http://52.76.46.177:8999/ec2/instance/event/start/'
            r_start = requests.get(url_instance_start)

        elif action == 'Terminate':
            pass
            url_instance_terminate = 'http://52.76.46.177:8999/ec2/instance/event/terminate/'
            r_terminate = requests.get(url_instance_terminate)

        else:
            response['message'] = 'Please specify a message'
            return render(requests, "Administrator/uploadcsv.html", response)

    except Exception as e:
        traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Administrator/uploadcsv.html", response)

    return render(requests,"Administrator/admindashboard.html",response)
