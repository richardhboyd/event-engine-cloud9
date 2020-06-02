# instance-resizer

ENV_NAME=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 12 | head -n 1)
OWNER_ARN=arn:aws:sts::603451405989:assumed-role/Feder08-RootRole-1HRX3XPC1PUFF/redirect_session
sam build && sam deploy && ENV_ID=$(aws cloud9 create-environment-ec2 --instance-type t2.micro --owner-arn $OWNER_ARN --name $ENV_NAME --output text --query "environmentId")