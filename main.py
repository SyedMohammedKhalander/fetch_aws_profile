import boto3

session = boto3.Session()

# access_key = 'YOUR_ACCESS_KEY'
# secret_key = 'YOUR_SECRET_KEY'
# 
# session = boto3.Session(
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key
# )

# can use the above commented line to get IAM username,arn and id by changing value of access_key and secret_key

iam_client = session.client('iam')

response = iam_client.get_user()


print("Local aws configure IAM user ID:", response['User']['UserId'])
print("Local aws configure IAM user Name:", response['User']['UserName'])
print("Local aws configure IAM user ARN:", response['User']['Arn'])
