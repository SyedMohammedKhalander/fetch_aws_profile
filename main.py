import boto3
from datetime import datetime, timedelta
import json

IAM_CLIENT = boto3.client('iam')
CLOUDTRAIL_CLIENT = boto3.client('cloudtrail')


def fetch_cloudtrail_create_events(username, start_time, end_time):
    filters = {'AttributeKey': 'ReadOnly', 'AttributeValue': "false"}
    events = []

    response = CLOUDTRAIL_CLIENT.lookup_events(
        LookupAttributes=[filters],
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=50
    )

    while response.get('NextToken') and len(
            events) < 2500:  # to get all events in last 7 days remove len(events) < 2500
        # but inturn it will take long time to fetch all the events i have added this u can remove this and run
        response = CLOUDTRAIL_CLIENT.lookup_events(
            LookupAttributes=[filters],
            StartTime=start_time,
            EndTime=end_time,
            MaxResults=50,
            NextToken=response.get('NextToken')
        )
        events.extend(response.get('Events'))

    create_events = [event for event in events if event_name_starts_with_create(event)]

    creat_events_by_user = [event for event in create_events if event.get("Username") and event.get("Username") == username]

    return creat_events_by_user

def fetch_cloudtrail_access_events(username, start_time, end_time):
    filters = {'AttributeKey': 'ReadOnly', 'AttributeValue': "true"}
    events = []

    response = CLOUDTRAIL_CLIENT.lookup_events(
        LookupAttributes=[filters],
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=50
    )

    while response.get('NextToken') and len(
            events) < 2500:  # to get all events in last 7 days remove len(events) < 2500
        # but inturn it will take long time to fetch all the events i have added this u can remove this and run
        response = CLOUDTRAIL_CLIENT.lookup_events(
            LookupAttributes=[filters],
            StartTime=start_time,
            EndTime=end_time,
            MaxResults=50,
            NextToken=response.get('NextToken')
        )
        events.extend(response.get('Events'))

    # create_events = [event for event in events if event_name_starts_with_create(event)]

    access_events_by_user = [event for event in events if event.get("Username") and event.get("Username") == username]

    return access_events_by_user


def event_name_starts_with_create(event):
    event_name = event.get('EventName', '')
    return 'Create' in event_name or event_name.startswith('Run')


def format_event_time(event):
    event['EventTime'] = event['EventTime'].isoformat()


def cleanup_event_data(event):
    keys_to_remove = ['ReadOnly', 'Resources', 'CloudTrailEvent', 'AccessKeyId']
    for key in keys_to_remove:
        if key in event:
            del event[key]


def fetch_and_store_aws_profile_details():
    session = boto3.Session()
    iam_client = session.client('iam')
    response = iam_client.get_user()
    create_date = response['User']['CreateDate']
    arn = response['User']['Arn']
    username = response['User']['UserName']
    access_key = response['User']['UserId']
    last_login = response['User']['PasswordLastUsed']

    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)
    start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = today.strftime('%Y-%m-%dT%H:%M:%SZ')

    cloudtrail_create_events = fetch_cloudtrail_create_events(username, start_time, end_time)
    cloudtrail_access_events = fetch_cloudtrail_access_events(username, start_time, end_time)
    for event in cloudtrail_create_events:
        format_event_time(event)
        cleanup_event_data(event)
    for event in cloudtrail_access_events:
        format_event_time(event)
        cleanup_event_data(event)

    data_to_store = {
        "created_date": create_date.isoformat(),
        "arn": arn,
        "user_name": username,
        "access_key": access_key,
        "last_login": last_login.isoformat(),
        "created_components": cloudtrail_create_events,
        "component_accessed": cloudtrail_access_events
    }

    json_data = json.dumps(data_to_store, indent=4)

    with open("user_data.json", "w") as json_file:
        json_file.write(json_data)

    print("User data stored in 'user_data.json'")


if __name__ == "__main__":
    fetch_and_store_aws_profile_details()
