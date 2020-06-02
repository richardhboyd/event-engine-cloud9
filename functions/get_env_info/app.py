def lambda_handler(event, context):
    environment_id = event["detail"]["tags"]["aws:cloud9:environment"]
    instance_id = event["resources"][0].split(":")[-1].split("/")[-1]
    environment_info = {
        "instance_id": instance_id,
        "environment_id": environment_id
    }
    return environment_info
