import boto3
import os
from configparser import ConfigParser

def load_aws_credentials(filepath):
    config = ConfigParser()
    config.read(filepath)
    return config

def fetch_profile_details(config, profile_name):
    return {
        'aws_access_key_id': config.get(profile_name, 'aws_access_key_id'),
        'aws_secret_access_key': config.get(profile_name, 'aws_secret_access_key')
    }

def fetch_aws_profile_details_from_local():
    credentials_path = os.path.expanduser("~") + '/.aws/credentials'
    config = load_aws_credentials(credentials_path)

    profile_details = {}

    for profile_name in config.sections():
        profile_details[profile_name] = fetch_profile_details(config, profile_name)

    config_path = os.path.expanduser("~") + '/.aws/config'
    config = load_aws_credentials(config_path)

    for profile_name in config.sections():
        if profile_name != 'default' and not profile_name.startswith("profile"):
            continue

        profile_name_dic = profile_name.replace("profile ", "", 1) if profile_name.startswith("profile") else profile_name
        profile_details[profile_name_dic] = {**profile_details.get(profile_name_dic, {}), 'region': config.get(profile_name, 'region', fallback=None),
                                             'output': config.get(profile_name, 'output', fallback=None)}

    return profile_details

def get_profile_details_from_aws(profile_details):
    session = boto3.Session(
        aws_access_key_id=profile_details['aws_access_key_id'],
        aws_secret_access_key=profile_details['aws_secret_access_key']
    )
    iam_client = session.client('iam')

    try:
        response = iam_client.get_user()
        return response['User']['Arn'], response['User']['UserName'], response['User']['CreateDate'], response['User']['PasswordLastUsed']
    except Exception as e:
        return None, None, None, None

def main():
    profiles = fetch_aws_profile_details_from_local()

    for profile_name, profile_details in profiles.items():
        print(f"{'Profile:':<20} {profile_name}")
        Arn, username, created_date, password_last_used = get_profile_details_from_aws(profile_details)
        valid = Arn is not None

        print(f"{'ValidProfile:':<20} {valid}")
        print(f"{'Access Key:':<20} {profile_details['aws_access_key_id']}")
        print(f"{'Secret Key:':<20} {profile_details['aws_secret_access_key']}")
        print(f"{'Region:':<20} {profile_details['region']}")
        print(f"{'Output:':<20} {profile_details['output']}")

        if valid:
            print(f"{'Arn:':<20} {Arn}")
            print(f"{'Username:':<20} {username}")
            print(f"{'Created Date:':<20} {created_date}")
            print(f"{'Password Last Used:':<20} {password_last_used}\n")
        print("-" * 40 + "\n")

if __name__ == "__main__":
    main()
