import boto3
import json

boto3.setup_default_session(profile_name='appvia')

import boto3
import json
from datetime import datetime

# Initialize AWS IAM client
iam_client = boto3.client('iam')
session = boto3.Session(profile_name='appvia')

# Get a list of all available AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

import boto3
import json
from datetime import datetime

# Initialize AWS IAM client
iam_client = boto3.client('iam')
session = boto3.Session(profile_name='appvia')

# Get a list of all available AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]


def list_iam_user():
    response = iam_client.list_users()

    # Initialize a dictionary to store IAM user data
    iam_users_data = {}

    # Iterate through the IAM users and gather required information
    for user in response['Users']:
        user_data = {
            "id": user['Arn'],
            "arn": user['Arn'],
            "accountId": user['UserId'],
            "name": user['UserName'],
            "path": user['Path'],
            "creationTime": user['CreateDate'].isoformat(),
            "accessKeyData": [],
            "mfaDevices": [],
            "virtualMfaDevices": [],
            "accessKeysActive": False,
            "passwordLastUsed": "",
            "passwordLastChanged": "",
            "passwordNextRotation": "",
            "passwordEnabled": False,
            "mfaActive": False,
            "groups": [],
            "inlinePolicies": [],
            "managedPolicies": [],
            "tags": []
        }

        access_keys = iam_client.list_access_keys(UserName=user['UserName'])
        for access_key in access_keys['AccessKeyMetadata']:
            user_data["accessKeyData"].append({
                "accessKeyId": access_key['AccessKeyId'],
                "status": access_key['Status'],
                "createDate": access_key['CreateDate'].isoformat(),
                "lastRotated": access_key['Status'] if 'Status' in access_key else ""
            })

        mfa_devices = iam_client.list_mfa_devices(UserName=user['UserName'])
        for mfa_device in mfa_devices['MFADevices']:
            user_data["mfaDevices"].append({
                "serialNumber": mfa_device['SerialNumber'],
                "enableDate": mfa_device['EnableDate'].isoformat()
            })

        virtual_mfa_devices = iam_client.list_virtual_mfa_devices(
            AssignmentStatus='Assigned'
        )

        for virtual_mfa_device in virtual_mfa_devices['VirtualMFADevices']:
            if virtual_mfa_device.get('User').get('UserName'):
                if virtual_mfa_device['User']['UserName'] == user['UserName']:
                    user_data["virtualMfaDevices"].append({
                        "serialNumber": virtual_mfa_device['SerialNumber'],
                        "enableDate": virtual_mfa_device['EnableDate'].isoformat()
                    })

        # Fetch user groups
        groups = iam_client.list_groups_for_user(UserName=user['UserName'])
        user_data["groups"] = [group['GroupName'] for group in groups['Groups']]

        # Fetch managed policies attached to the user
        attached_policies = iam_client.list_attached_user_policies(UserName=user['UserName'])
        user_data["managedPolicies"] = [{
            "policyArn": policy['PolicyArn'],
            "policyName": policy['PolicyName']
        } for policy in attached_policies['AttachedPolicies']]

        # Fetch tags for the user
        tags = iam_client.list_user_tags(UserName=user['UserName'])
        user_data["tags"] = [{
            "key": tag['Key'],
            "value": tag['Value']
        } for tag in tags['Tags']]

        # Append user data to the dictionary
        iam_users_data[user['UserName']] = user_data

    return iam_users_data


def list_alb():
    global regions
    alb_data = {}
    for region in regions:
        elbv2 = boto3.client('elbv2', region_name=region)
        response = elbv2.describe_load_balancers()

        alb_data[region] = []

        for alb in response['LoadBalancers']:
            alb_data[region].append(alb)

    return alb_data


def list_security_groups():
    global regions
    all_security_groups = {}
    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)

        # Get a list of security groups in the current region
        security_groups = ec2_client.describe_security_groups()['SecurityGroups']

        # Append security group details to the dictionary
        all_security_groups[region] = security_groups

    return all_security_groups


def list_ec2_instances():
    global regions

    instances_by_region = {}
    for region in regions:
        ec2_client = session.client('ec2', region_name=region)
        instances = ec2_client.describe_instances()
        instances_by_region[region] = instances['Reservations']

    instances_data = {}
    for region in regions:
        instances_data[region] = []
        for reservation in instances_by_region[region]:
            for instance in reservation['Instances']:
                instances_data[region].append(instance)

    return instances_data


def list_vpcs():
    vpcs_by_region = {}

    for region in regions:
        ec2_client = session.client('ec2', region_name=region)
        vpcs = ec2_client.describe_vpcs()
        vpcs_by_region[region] = vpcs['Vpcs']

    vpc_data = {}

    for region in regions:
        vpc_data[region] = []

        for vpc in vpcs_by_region[region]:
            vpc_data[region].append({
                "VpcId": vpc['VpcId'],
                "CidrBlock": vpc['CidrBlock'],
                "IsDefault": vpc['IsDefault'],
                # Add more VPC attributes here as needed
            })

    return vpc_data


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


def list_s3_buckets():
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    s3_data = {}
    for bucket_info in response['Buckets']:
        bucket_name = bucket_info['Name']
        object_list = s3_client.list_objects_v2(Bucket=bucket_name)

        object_data = []

        for s3_object in object_list.get('Contents', []):
            object_data.append({
                "Key": s3_object['Key'],
                "Size": s3_object['Size'],
                "LastModified": s3_object['LastModified'].isoformat(),
                "ETag": s3_object['ETag']
            })

        s3_data[bucket_name] = object_data

    return s3_data


def list_ecr_repositories():
    global regions
    ecr_data = {}
    for region in regions:
        ecr = boto3.client('ecr', region_name=region)
        response = ecr.describe_repositories()

        ecr_data[region] = []

        for repository in response['repositories']:
            ecr_data[region].append(repository)

    return ecr_data


def list_acm():
    global regions
    acm_data = {}
    for region in regions:
        acm_client = boto3.client('acm', region_name=region)
        response = acm_client.list_certificates()

        acm_data[region] = []

        for certificate in response['CertificateSummaryList']:
            acm_data[region].append(certificate)

    return acm_data


def list_cloud9():
    global regions
    cloud9_data = {}
    for region in regions:
        cloud9_client = boto3.client('cloud9', region_name=region)
        response = cloud9_client.list_environments()

        cloud9_data[region] = []

        for environment in response['environmentIds']:
            cloud9_data[region].append(environment)

    return cloud9_data


def list_cloudfront():
    global regions
    cloudfront_data = {}
    for region in regions:
        cloudfront_client = boto3.client('cloudfront', region_name=region)
        response = cloudfront_client.list_distributions()

        cloudfront_data[region] = []

        for distribution in response.get('DistributionList', {}).get('Items', []):
            cloudfront_data[region].append(distribution)

    return cloudfront_data


def list_cloudtrail():
    global regions
    cloudtrail_data = {}
    for region in regions:
        cloudtrail_client = boto3.client('cloudtrail', region_name=region)
        response = cloudtrail_client.describe_trails()

        cloudtrail_data[region] = []

        for trail in response.get('trailList', []):
            cloudtrail_data[region].append(trail)

    return cloudtrail_data


def list_cloudwatch():
    global regions
    cloudwatch_data = {}
    for region in regions:
        cloudwatch_client = boto3.client('cloudwatch', region_name=region)

        alarms_response = cloudwatch_client.describe_alarms()
        cloudwatch_data[region] = {"alarms": alarms_response.get("MetricAlarms", [])}

        dashboards_response = cloudwatch_client.list_dashboards()
        cloudwatch_data[region]["dashboards"] = dashboards_response.get("DashboardEntries", [])

    return cloudwatch_data


def list_codebuild():
    global regions
    codebuild_data = {}
    for region in regions:
        codebuild_client = boto3.client('codebuild', region_name=region)
        response = codebuild_client.list_projects()

        codebuild_data[region] = []

        for project in response.get('projects', []):
            codebuild_data[region].append(project)

    return codebuild_data


def list_dynamodb():
    global regions
    dynamodb_data = {}
    for region in regions:
        dynamodb_client = boto3.client('dynamodb', region_name=region)
        tables_response = dynamodb_client.list_tables()

        dynamodb_data[region] = {"tables": tables_response.get("TableNames", [])}

    return dynamodb_data


def list_ebs():
    global regions
    ebs_data = {}
    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        volumes_response = ec2_client.describe_volumes()

        ebs_data[region] = {"volumes": volumes_response.get("Volumes", [])}

    return ebs_data


def list_efs():
    global regions
    efs_data = {}
    for region in regions:
        efs_client = boto3.client('efs', region_name=region)
        file_systems_response = efs_client.describe_file_systems()

        efs_data[region] = {"file_systems": file_systems_response.get("FileSystems", [])}

    return efs_data


def list_kms():
    global regions
    kms_data = {}
    for region in regions:
        kms_client = boto3.client('kms', region_name=region)
        keys_response = kms_client.list_keys()

        kms_data[region] = {"keys": keys_response.get("Keys", [])}

    return kms_data


def list_lambda():
    global regions
    lambda_data = {}
    for region in regions:
        lambda_client = boto3.client('lambda', region_name=region)
        functions_response = lambda_client.list_functions()

        lambda_data[region] = {"functions": functions_response.get("Functions", [])}

    return lambda_data


def list_ses():
    global regions
    ses_data = {}
    for region in regions:
        ses_client = boto3.client('ses', region_name=region)
        identities_response = ses_client.list_identities()

        ses_data[region] = {"identities": identities_response.get("Identities", [])}

    return ses_data


def list_sns():
    global regions
    sns_data = {}
    for region in regions:
        sns_client = boto3.client('sns', region_name=region)
        topics_response = sns_client.list_topics()

        sns_data[region] = {"topics": topics_response.get("Topics", [])}

    return sns_data


def list_sqs():
    global regions
    sqs_data = {}
    for region in regions:
        sqs_client = boto3.client('sqs', region_name=region)
        queues_response = sqs_client.list_queues()

        sqs_data[region] = {"queues": queues_response.get("QueueUrls", [])}

    return sqs_data

def list_rds_instances():
    rds_instances_by_region = {}

    for region in regions:
        rds_client = session.client('rds', region_name=region)
        rds_instances = rds_client.describe_db_instances()
        rds_instances_by_region[region] = rds_instances['DBInstances']

    rds_data = {}

    for region in regions:
        rds_data[region] = []

        for rds_instance in rds_instances_by_region[region]:
            rds_data[region].append({
                "DBInstanceIdentifier": rds_instance['DBInstanceIdentifier'],
                "DBInstanceClass": rds_instance['DBInstanceClass'],
                "Engine": rds_instance['Engine'],
            })

    return rds_data


def list_vpc_endpoints():
    vpc_endpoints_by_region = {}

    for region in regions:
        ec2_client = session.client('ec2', region_name=region)
        vpc_endpoints = ec2_client.describe_vpc_endpoints()
        vpc_endpoints_by_region[region] = vpc_endpoints['VpcEndpoints']

    return vpc_endpoints_by_region

def main():
    data = {
        # "s3": list_s3_buckets(),
        # "iam": list_iam_user(),
        # "alb": list_alb(),
        # "security_groups": list_security_groups(),
        # "ec2_instances": list_ec2_instances(),
        # "ecr_repositories": list_ecr_repositories(),
        # "acm": list_acm(),
        # "cloud9": list_cloud9(),
        # "cloudfront": list_cloudfront(),
        # "cloudtrail": list_cloudtrail(),
        # "cloudwatch": list_cloudwatch(),
        # "codebuild": list_codebuild(),
        # "ebs": list_ebs(),
        # "efs": list_efs(),
        # "kms": list_kms(),
        # "lambda": list_lambda(),
        # "ses": list_ses(),
        # "sns": list_sns(),
        # "sqs": list_sqs(),
        # "vpc": list_vpcs(),
        # "rds": list_rds_instances()
        "vpcEndpoints": list_vpc_endpoints()

    }

    # Create a JSON file and store all the data
    with open('aws_data1.json', 'w') as json_file:
        json.dump(data, json_file, indent=4, cls=DateTimeEncoder)


if __name__ == "__main__":
    main()
