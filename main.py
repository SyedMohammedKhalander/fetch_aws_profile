import boto3
import os
from configparser import ConfigParser
import json
from datetime import datetime

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

def get_profile_details_from_config_files_in_local():
    profiles = fetch_aws_profile_details_from_local()
    output_file_path = "profile_details.json"
    with open(output_file_path, "w") as output_file:
        profile_data = []
        for profile_name, profile_details in profiles.items():
            data = {
                "profile_name": profile_name,
                "aws_access_key_id": profile_details['aws_access_key_id'],
                # "aws_secret_access_key": profile_details['aws_secret_access_key'],
                "region": profile_details['region'],
                "output": profile_details['output']
            }
            Arn, username, created_date, password_last_used = get_profile_details_from_aws(profile_details)
            valid = Arn is not None

            data["valid_profile"] = valid
            if valid:
                data["arn"] = Arn
                data["username"] = username
                data["created_date"] = created_date.isoformat()  # Convert datetime to string
                if password_last_used is not None:
                    data["password_last_used"] = password_last_used.isoformat()  # Convert datetime to string

            profile_data.append(data)

        json.dump(profile_data, output_file, indent=4)
        print("Data saved to", output_file_path)


def get_profile_details_from_key_and_secret(key, secret):
    import boto3

    access_key = key
    secret_key = secret

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    iam_client = session.client('iam')
    file_path = "user_data.json"
    response = iam_client.get_user()
    data = {
        "aws_access_key_id": response['User']['UserId'],
        "arn": response['User']['Arn'],
        "username": response['User']['UserName'],
        "created_date": response['User']['CreateDate'].isoformat(),  # Convert datetime to string
        "password_last_used": response['User']['PasswordLastUsed'].isoformat()  # Convert datetime to string
    }
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Data saved to", file_path)


def main(key=None, secret=None):
    if key == None or secret == None:
        get_profile_details_from_config_files_in_local()
    else:
        get_profile_details_from_key_and_secret(key, secret)

if __name__ == '__main__':
    main(key=None, secret=None)
