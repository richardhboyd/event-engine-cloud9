import boto3
import json
import os
from time import sleep
iam_client= boto3.client('iam')
ec2_client = boto3.client('ec2')

def build_arn(profile_name: str) -> str:
    # arn:aws:iam::603451405989:instance-profile/1baddb0543f54068a3bbd82df5944c6a-InstanceProfile
    account_id = boto3.client('sts').get_caller_identity()['Account']
    return f'arn:aws:iam::{account_id}:instance-profile/{profile_name}'

def lambda_handler(event, context):
    print(event)
    instance_id = event["instance_id"]
    environment_id = event["environment_id"]
    role_name = f'cloud9-profile-{environment_id}'
    # instance_profile_name = f'{environment_id}-InstanceProfile'
    instance_profile_name = f'cloud9-profile-{environment_id}'

    try:
        iam_client.create_role(
            Path='/',
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(
                {
                    'Version': '2012-10-17',
                    'Statement': {
                        'Effect': 'Allow',
                        'Principal': {'Service': 'ec2.amazonaws.com'},
                        'Action': 'sts:AssumeRole'
                    }
                }),
            Description='EC2 Instance Profile Role'
        )
        sleep(30)
    except iam_client.exceptions.EntityAlreadyExistsException as _:
        pass
    try:
        policy_arn = os.environ['PolicyArn']
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
    except Exception as _:
        pass
    try:
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        )
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy'
        )
    except Exception as e:
        raise e
    try:
        create_instance_profile_response = iam_client.create_instance_profile(InstanceProfileName=instance_profile_name)
        print(create_instance_profile_response)
        instance_profile_arn = create_instance_profile_response['InstanceProfile']['Arn']
        sleep(30)
    except iam_client.exceptions.EntityAlreadyExistsException as _:
        instance_profile_arn = build_arn(instance_profile_name)
    try:
        response = iam_client.add_role_to_instance_profile(
            InstanceProfileName=instance_profile_name,
            RoleName=role_name
        )
        print(response)
        response = ec2_client.associate_iam_instance_profile(
            IamInstanceProfile={'Name': instance_profile_name},
            InstanceId=instance_id
        )
        print(response)
    except iam_client.exceptions.LimitExceededException as e:
        print(e)
    
    
    response = ec2_client.describe_iam_instance_profile_associations(Filters=[{'Name': 'instance-id','Values': [instance_id]},{'Name': 'state','Values': ['associated']}])
    print(response)
    while len(response['IamInstanceProfileAssociations']) < 1:
        print("waiting for association to finish")
        sleep(30)
        response = ec2_client.describe_iam_instance_profile_associations(Filters=[{'Name': 'instance-id','Values': [instance_id]},{'Name': 'state','Values': ['associated']}])

    print("Stopping instance")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

    environment_info = {
        "instance_id": instance_id,
        "environment_id": environment_id,
        "role_name": role_name,
        "instance_profile_name": instance_profile_name
    }
    return environment_info
