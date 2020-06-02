import boto3
import os
ec2_client= boto3.client('ec2')

def lambda_handler(event, context):
    print(event)
    instance_id = event["instance_id"]
    environment_id = event["environment_id"]
    instance = ec2_client.describe_instances(Filters=[{'Name': 'instance-id', 'Values': [instance_id]}])['Reservations'][0]['Instances'][0]
    block_volume_id = instance['BlockDeviceMappings'][0]['Ebs']['VolumeId']
    ec2 = boto3.resource('ec2')
    volume = ec2.Volume(block_volume_id)
    if volume.size != int(os.environ.get('VolumeSize', '50')):
        try:
            ec2_client.modify_volume(VolumeId=block_volume_id,Size=int(os.environ.get('VolumeSize', '50')))
        except Exception as e:
            print(e)
            raise e
    
    environment_info = {
        "instance_id": instance_id,
        "environment_id": environment_id
    }
    return environment_info
