import traceback
import requests as req
from django.shortcuts import render
from Module_DeploymentMonitoring.models import *

def run_UAT_Process(requests):
    response = {}

    action = requests.GET.get('action')
    SECRET_KEY = 'm0nKEY'
    IMAGE_ID = 'ami-0b278e601db41f051'
    SNAPSHOT_ID = 'snap-054b5b44115032c6e'
    count = 5

    try:
        if action == 'Launch':
            url_elastic_ip_retrieve = 'http://52.76.46.177:8999/ec2/elastic_ip/list/'
            url_instance_launch = 'http://52.76.46.177:8999/ec2/instance/event/launch/'
            payload = {'secret_key':SECRET_KEY, 'image_id':IMAGE_ID, 'snapshot_id':SNAPSHOT_ID, 'count':count}

            r_instance = req.get(url_instance_launch, params=payload)
            res = r_instance.json()
            print(res)

            for instance in res['instance_ids']:
                try:
                    instanceObj = Instance.objects.create(
                        instance_id=instance['instance_id']
                    )
                    instanceObj.save()
                except:
                    pass

            r_ids = req.get(url_elastic_ip_retrieve)
            res = r_ids.json()

            ips = []
            if len(res['Elastic_IPs']['Unassgined']) > 0:
                for elastic_ip in res['Elastic_IPs']['Unassgined']:
                    ips.append(elastic_ip['AllocationId'])

            for x in range(0,len(ips)):
                allocation_id = ips[x]
                try:
                    ipsObj = Elastic_IPs.objects.create(
                        id=x+1,
                        allocation_id=allocation_id,
                    )
                    ipsObj.save()
                except:
                    pass

        elif action == 'Stop':
            instances = Instance.objects.all()
            count = 1
            for instance in instances:
                try:
                    elastic_ipObj = Elastic_IPs.objects.get(id=count)
                    allocation_id = elastic_ipObj.allocation_id
                    count += 1
                except:
                    pass

                url_elastic_ip_associate = 'http://52.76.46.177:8999/ec2/elastic_ip/associate/'
                payload = {'instance_id':instance.instance_id, 'allocation_id':allocation_id}

                r_ips = req.get(url_elastic_ip_associate, params=payload)
                res = r_ips.json()

                instance.public_ip = res['Response']['instance_public_ip']
                instance.save()

                url_instance_stop = 'http://52.76.46.177:8999/ec2/instance/event/stop/'
                payload = {'instance_id':instance.instance_id, 'secret_key':SECRET_KEY,}
                r_stop = req.get(url_instance_stop, params=payload)

        elif action == 'Start':
            instances = Instance.objects.all()
            for instance in instances:
                url_instance_start = 'http://52.76.46.177:8999/ec2/instance/event/start/'
                payload = {'instance_id':instance.instance_id, 'secret_key':SECRET_KEY,}
                r_start = req.get(url_instance_start, params=payload)

        elif action == 'Terminate':
            instances = Instance.objects.all()
            for instance in instances:
                url_instance_terminate = 'http://52.76.46.177:8999/ec2/instance/event/terminate/'
                payload = {'instance_id':instance.instance_id, 'secret_key':SECRET_KEY,}
                r_terminate = req.get(url_instance_terminate, params=payload)

            Instance.objects.all().delete()
            Elastic_IPs.objects.all().delete()

        else:
            response['message'] = 'Please specify a message'
            return render(requests, "Administrator/uploadcsv.html", response)

    except Exception as e:
        traceback.print_exc()
        response['message'] = e.args[0]
        return render(requests, "Administrator/uploadcsv.html", response)

    return render(requests,"Administrator/admindashboard.html",response)
