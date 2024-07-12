import argparse
import subprocess
import json
import boto3
import botocore.exceptions
import os

parser = argparse.ArgumentParser(description="Deploy services using Serverless and AWS.")
parser.add_argument("--stage", default="dev", help="Set the stage for the deployment")
parser.add_argument("--profile", default="default", help="Set the AWS profile")
parser.add_argument("--region", required=False, default="us-east-1", help="Set the AWS region")
parser.add_argument("--ci", required=False, default="false", help="Set if it's working as CI")


aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_session_token = os.environ['AWS_SESSION_TOKEN']

args = parser.parse_args()

if args.ci == 'true':
    boto3.setup_default_session(    
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=args.region,
        aws_session_token=aws_session_token
    )
else:
    boto3.setup_default_session(profile_name=args.profile, region_name=args.region)

lexCLient = boto3.client('lexv2-models')

sts = boto3.client("sts")
account_id = sts.get_caller_identity()["Account"]


def get_stack_outputs(stage):
    stack_name = f"mazama-ace-ai-{stage}"
    client = boto3.client('cloudformation')

    stack_info = client.describe_stacks(StackName=stack_name)
    outputs = stack_info['Stacks'][0]['Outputs']

    print(outputs)

    bot_id = ""
    lambda_arn = ""

    for output in outputs:
        if output['OutputKey'] == 'BotId':
            bot_id = output['OutputValue']
        elif output['OutputKey'] == 'RouterLambdaFunctionQualifiedArn':
            lambda_arn = output['OutputValue']

    return bot_id, lambda_arn


def get_bot_alias_arn(bot_id, bot_alias_name):
    try:
        response = lexCLient.describe_bot_alias(botId=bot_id, botAliasId=bot_alias_name)
        return { 
            'botAliasId': response['botAliasId'],
            'botAliasName': response['botAliasName'],
            'botVersion': response['botVersion'],
        }
    except Exception as e:
        print(f"Error obtaining bot alias: {e}")
        return None

def main():

    command = ["sls", "deploy", "--config", "pre-deploy.yml", "--stage", args.stage]

    if not args.ci == 'true':
        command += ["--aws-profile", args.profile]

    # Deploy with Serverless using specific configuration
    subprocess.run(command , check=True)
    # Copy lex.zip file to S3
    s3_bucket = f"s3://{account_id}-spark-mentor-chatbot-bucket-{args.stage}/"
    
    
    command =["aws", "s3", "cp", "./bot/lex.zip", s3_bucket]

    if not args.ci == 'true':
        command += ["--profile", args.profile]

    subprocess.run(command, check=True)
    # Final Serverless deployment

    command = ["sls", "deploy", "--stage", args.stage]

    if not args.ci == 'true':
        command += ["--aws-profile", args.profile]
    subprocess.run(command, check=True)
    bot_alias_id = 'TSTALIASID'

    bot_id, lambda_arn = get_stack_outputs(args.stage)
    bot_info = get_bot_alias_arn(bot_id, bot_alias_id)


    splitted_arn = lambda_arn.split(':')
    
    # La última parte es la versión
    lambda_arn = ':'.join(splitted_arn[:-1])
    print(json.dumps(bot_info, indent=4))



    print(json.dumps({
        "bot_alias_id": bot_alias_id,
        "lambda_arn": lambda_arn,
        "bot_id": bot_id,
        "account_id": account_id,
    }, indent=4))

    #Assign function to bot
    print("Attaching lambda to bot")
    response = lexCLient.update_bot_alias(
        botAliasId=bot_info['botAliasId'],
        botAliasName=bot_info['botAliasName'],
        botVersion= bot_info['botVersion'],
        botAliasLocaleSettings={
            'en_US': {
                'enabled': True,
                'codeHookSpecification': {
                    'lambdaCodeHook': {
                        'lambdaARN': lambda_arn,
                        'codeHookInterfaceVersion': '1.0'
                    }
            }
                }
        },
        botId=bot_id

    )
    
    print(response)

    lambdaClient = boto3.client('lambda')
    
    try:

        print("Attaching permission to lex to execute lambdas")
        response = lambdaClient.add_permission(
            FunctionName=f"mazama-ace-ai-{args.stage}-Router",
            StatementId="chatbot-fulfillment",
            Action='lambda:InvokeFunction',
            Principal='lex.amazonaws.com',
            SourceArn=f"arn:aws:lex:us-east-1:{account_id}:bot-alias/{bot_id}/{bot_alias_id}",
        )
        
        print(response)

        print("Building bot for first time")
        
        response = lexCLient.build_bot_locale(
            botId=bot_id,
            botVersion=bot_info['botVersion'],
            localeId='en_US'
        )

        print(response)
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ResourceConflictException':
            print("Lambdas already attached")
        else:
            
            print(f"There's unexpected error: {error}")


if __name__ == "__main__":
    main()