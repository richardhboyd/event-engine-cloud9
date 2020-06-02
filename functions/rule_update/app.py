import boto3
import json
import cfnresponse
import os

def lambda_handler(event, context):
  try:
    client = boto3.client('events')
    response = client.describe_rule(Name=os.environ.get('RuleName'))
    json_event = json.loads(response['EventPattern'])
    json_event['detail']['version'] = [1]
    response = client.put_rule(Name=response['Name'],EventPattern=json.dumps(json_event),State=response['State'])
    cfnresponse.send(event, context, cfnresponse.SUCCESS, response, event["RequestId"])
  except Exception as _:
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, event["RequestId"])
