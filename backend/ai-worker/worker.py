import os
import time
import urllib.parse
import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event,context):

    for record in event.get("Records",[]):
        raw_key = record["s3"]["object"]["key"]
        s3_key = urllib.parse.unquote_plus(raw_key)

        print(f"Processing file: {s3_key}")

        parts = s3_key.split("/")
        if len(parts) !=3:
            print(f"Skipping wrong path: {s3_key}")
            continue

        _, user_id, image_id = parts


        table.update_item(
            Key={
                "pk": f"USER#{user_id}",
                "sk": f"IMAGE#{image_id}"
            },

            UpdateExpression="SET #st= :status, character_name= :char, updated_at= :now",
            ExpressionAttributeNames={
                "#st": "status"
            },
            ExpressionAttributeValues={
                ":status": "Done",
                ":char": "Luffy",
                ":now" : int(time.time())
            }
        )
        print(f"Updated image {s3_key} is complete")

    return {
    "statusCode":200,
    "status":"success",
    }
