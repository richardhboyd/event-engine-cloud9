import boto3

def lambda_handler(event, context):
    command_id = event["command_id"]
    instance_id = event["instance_id"]
    ssm_client = boto3.client('ssm')
    response = ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
    if response['Status'] in ['Pending', 'InProgress', 'Delayed']:
        raise Exception("Command in Progress")
    else:
        return
