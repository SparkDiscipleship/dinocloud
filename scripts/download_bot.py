import argparse
import boto3
import requests
import os

def download_lex_export(bot_id, bot_alias, aws_profile, destination_path, region):
    session = boto3.Session(
        profile_name=aws_profile,
        region_name=region)
    lex_client = session.client('lexv2-models')

    export_job_response = lex_client.create_export(
        resourceSpecification={
            'botExportSpecification': {
                'botId': bot_id,
                'botVersion': "DRAFT",
            }
        },
        fileFormat='LexJson'
    )
    exportId = export_job_response['exportId']

    waiter = lex_client.get_waiter('bot_export_completed')

    waiter.wait(exportId=exportId)



    export_response = lex_client.describe_export(exportId=exportId)


    export_url = export_response['downloadUrl']
    
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Download the file using 'requests'
    response = requests.get(export_url)
    
    with open(os.path.join(destination_path, "lex.zip"), 'wb') as file:
        file.write(response.content)

# Parse arguments from command line
parser = argparse.ArgumentParser(description='Download a Lex bot export.')
parser.add_argument('--botID', required=True, help='The Bot ID.')
parser.add_argument('--botAlias', required=True, help='The Bot Alias.')
parser.add_argument('--profile', required=True, help='AWS CLI profile name.')
parser.add_argument('--region', required=False, help='AWS region name.', default='us-east-1')

args = parser.parse_args()

destination_path = 'bot'

download_lex_export(args.botID, args.botAlias, args.profile, destination_path, args.region)