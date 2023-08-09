import boto3
import os
from configparser import ConfigParser

def fetch_aws_profile_details_from_local():
    # Load the AWS credentials file
    config = ConfigParser()

    config.read(os.path.expanduser("~")+'/.aws/credentials')  # You might need to provide the full path

    # Fetch all profile names
    profile_names = config.sections()

    # Create a dictionary to store profile details
    profile_details = {}

    # Iterate through profiles and fetch details
    for profile_name in profile_names:
        profile_details[profile_name] = {
            'aws_access_key_id': config.get(profile_name, 'aws_access_key_id'),
            'aws_secret_access_key': config.get(profile_name, 'aws_secret_access_key')
        }

    config.read(os.path.expanduser("~") + '/.aws/config')  # You might need to provide the full path

    # Fetch all profile names
    profile_names = config.sections()

    for profile_name in profile_names:
        if profile_name != 'default' and not profile_name.startswith("profile"):
            continue
        if profile_name.startswith("profile"):
            profile_name_dic = profile_name.replace("profile ", "", 1)
            dict1 = profile_details[profile_name_dic]
            dict2 = {
                'region': config.get(profile_name, 'region', fallback=None),
                'output': config.get(profile_name, 'output', fallback=None)
            }
        else:
            profile_name_dic = profile_name
            dict1 = profile_details[profile_name]
            dict2 = {
                'region': config.get(profile_name, 'region', fallback=None),
                'output': config.get(profile_name, 'output', fallback=None)
            }
        profile_details[profile_name_dic] = {**dict1, **dict2}


    return profile_details

def get_profile_details_from_aws(profile_details):
    session = boto3.Session(
        aws_access_key_id=profile_details['aws_access_key_id'],
        aws_secret_access_key=profile_details['aws_secret_access_key']
    )
    iam_client = session.client('iam')

    response = iam_client.get_user()

    return response['User']['Arn'],response['User']['UserName'], response['User']['CreateDate'], response['User']['PasswordLastUsed']

profiles = fetch_aws_profile_details_from_local()
for profile_name, profile_details in profiles.items():
    print(f"{'Profile:':<20} {profile_name}")
    valid = True
    try:
        Arn, username, created_date, password_last_used = get_profile_details_from_aws(profile_details)
    except:
        valid = False
        print(f"{'ValidProfile:':<20} {valid}")
        print(f"{'Access Key:':<20} {profile_details['aws_access_key_id']}")
        print(f"{'Secret Key:':<20} {profile_details['aws_secret_access_key']}")
        print(f"{'Region:':<20} {profile_details['region']}")
        print(f"{'Output:':<20} {profile_details['output']}\n")
        continue
    print(f"{'ValidProfile:':<20} {valid}")
    print(f"{'Arn:':<20} {Arn}")
    print(f"{'Username:':<20} {username}")
    print(f"{'Access Key:':<20} {profile_details['aws_access_key_id']}")
    print(f"{'Secret Key:':<20} {profile_details['aws_secret_access_key']}")
    print(f"{'Region:':<20} {profile_details['region']}")
    print(f"{'Created Date:':<20} {created_date}")
    print(f"{'Password Last Used:':<20} {password_last_used}")
    print(f"{'Output:':<20} {profile_details['output']}\n")
    print("-" * 40+"\n")