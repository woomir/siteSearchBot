import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from boto3.dynamodb.conditions import Key

AWS_ACCESS_KEY_ID = "AKIA5CMUDBP7VTOBN4EG"
AWS_SECRET_ACCESS_KEY = "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"
AWS_DEFAULT_REGION = "ap-northeast-2"
campName = ['울주해양레포츠센터', '대저캠핑장', '삼락캠핑장']

session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)


def dbScan(dynamodb=None):
    dynamodb = session.resource('dynamodb')  # bucket 목록
    table = dynamodb.Table('siteSearchBot_campInfo')

    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Items']


if __name__ == '__main__':
    campDb = dbScan()
    if campDb:
        print("Get campDb succeeded:")
        pprint(campDb[0]['selectedDate'][0]['startDate'], sort_dicts=False)
