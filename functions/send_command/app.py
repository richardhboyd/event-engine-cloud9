import boto3
import json
import os
from io import BytesIO
ssm_client = boto3.client('ssm')
s3_resource = boto3.resource('s3')

def get_preamble():
    return """
if [ $(readlink -f /dev/xvda) = "/dev/xvda" ]
then
  # Rewrite the partition table so that the partition takes up all the space that it can.
  sudo growpart /dev/xvda 1
  # Expand the size of the file system.
  sudo resize2fs /dev/xvda1
else
  # Rewrite the partition table so that the partition takes up all the space that it can.
  sudo growpart /dev/nvme0n1 1
  # Expand the size of the file system.
  sudo resize2fs /dev/nvme0n1p1
fi
"""

def ssm_ready(ssm_client, instance_id):
    try:
        response = ssm_client.describe_instance_information(Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}])
        return len(response['InstanceInformationList'])>=1
    except ssm_client.exceptions.InvalidInstanceId:
        return False

def instance_ready(instance_id):
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    try:
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
    except Exception as e:
        print(e)
        return False
    if state == 'stopped':
        print("restarting instance")
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        return False
    if state in ['stopping', 'pending']:
        return False
    if state == 'running':
        return True
    raise Exception("IDK what's happening")

def lambda_handler(event, context):
    print(event)
    instance_id = event["instance_id"]
    environment_id = event["environment_id"]
    role_name = event["role_name"]
    instance_profile_name = event['instance_profile_name']
    
    if not instance_ready(instance_id):
        raise Exception("Instance not ready yet")
    
    if not ssm_ready(ssm_client, instance_id):
        raise Exception("We're not ready yet")

    try:
        print(os.environ["S3Bucket"])
        print(os.environ["S3Object"])
        bucket = s3_resource.Bucket(os.environ["S3Bucket"])
        obj = bucket.Object(os.environ["S3Object"])
        output = BytesIO()
        obj.download_fileobj(output)
        commands = get_preamble() + '\n' + output.getvalue().decode('utf-8') + '\n'
    except Exception as e:
        print(e)
        commands = get_preamble()

    send_command_response = ssm_client.send_command(
        InstanceIds=[instance_id], 
        DocumentName='AWS-RunShellScript', 
        Parameters={'commands': commands.split('\n')},
        CloudWatchOutputConfig={
            'CloudWatchLogGroupName': f'ssm-output-{instance_id}',
            'CloudWatchOutputEnabled': True
        }
    )

    environment_info = {
        "instance_id": instance_id,
        "environment_id": environment_id,
        "role_name": role_name,
        "instance_profile_name": instance_profile_name,
        "command_id": send_command_response['Command']['CommandId']
    }
    return environment_info
