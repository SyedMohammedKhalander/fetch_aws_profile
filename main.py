import boto3

session = boto3.Session()

iam_client = session.client('iam')

response = iam_client.get_user()

print("User ARN:", response['User']['Arn'])
print("User Name:", response['User']['UserName'])
print("User ID:", response['User']['UserId'])