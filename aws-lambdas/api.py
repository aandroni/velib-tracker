import boto3
import json

# DynamoDB table name
TABLE_NAME = "bikes"

db = boto3.resource("dynamodb")
table = db.Table(TABLE_NAME)

# Connect to DynamoDB
def api(event, context):
    '''
    AWS Lambda function for the 'bikes' API
    '''
    # Get data from DynamoDB table
    response = table.scan()

    # Convert dictionary values to int (needed to serialize to JSON)
    convert_value_to_int = lambda item: {k: int(v) for k, v in item.items()}
    items = [convert_value_to_int(item) for item in response["Items"]]

    return {
        "statusCode": 200,
        "body": json.dumps(items)
    }
