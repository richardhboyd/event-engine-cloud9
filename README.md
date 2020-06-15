# Cloud9 Environment bootstrapper
Once the template is deployed, you can test new environments being updated with the following command.
````bash
ENV_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 12 | head -n 1)
OWNER_ARN=[your ARN here]
sam deploy --guided
ENV_ID=$(aws cloud9 create-environment-ec2 --instance-type t2.micro --owner-arn $OWNER_ARN --name $ENV_NAME --output text --query "environmentId")
````
