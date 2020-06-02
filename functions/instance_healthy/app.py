import boto3
import time

c9_client = boto3.client("cloud9")
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    instance_id = event['instance_id']
    environment_id = event['environment_id']
    

    environment_status = c9_client.describe_environment_status(environmentId=environment_id)
    instance_status = ec2_client.describe_instances(InstanceIds=[instance_id])
    try:
        state = instance_status['Reservations'][0]['Instances'][0]['State']['Name']
    except Exception as _:
        state = 'UNKNOWN'
    
    while environment_status['status'] != 'ready' and state != 'running':
        print("sleeping")
        time.sleep(10)
        environment_status = c9_client.describe_environment_status(environmentId=environment_id)
        instance_status = ec2_client.describe_instances(InstanceIds=[instance_id])
        try:
            state = instance_status['Reservations'][0]['Instances'][0]['State']['Name']
        except Exception as e:
            print(e)
            state = 'UNKNOWN'
    
    
    environment_info = {
        "instance_id": instance_id,
        "environment_id": environment_id
    }
    return environment_info
