import json
import os
import time
import uuid
import boto3
from botocore.config import Config
import base64

BUCKET_NAME = os.environ['BUCKET_NAME']
TABLE_NAME = os.environ['TABLE_NAME']

s3_client = boto3.client("s3", config=Config(signature_version="s3v4"))
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


# reading user id from jwt token
def get_user_id(event):
    try:
        auth = event.get("headers", {}).get("authorization", "")
        token = auth.replace("Bearer", "").strip()
        payload = token.split(".")[1] + "=="
        claims = json.loads(base64.urlsafe_b64decode(payload))
        return claims.get("sub")
    except Exception:
        return None
        


def lambda_handler(event,context):
    user_id = get_user_id(event)
    if not user_id:
        return{
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Please login first"})
        }

    http_method = event.get("requestContext",{}).get("http",{}).get("method", "")

    if http_method == "GET":
        image_id = event.get("pathParameters",{}).get("image_id")

        responce = table.get_item(
            Key={
                "pk": f"USER#{user_id}",
                "sk": f"IMAGE#{image_id}"
            }
        )
        item = responce.get("Item")

        if not item:
            return{
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Upload not found"})
            }

        return{
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "image_id": image_id,
                    "status": item.get("status"),
                    "character_name": item.get("character_name")
                }
            )
        }







    image_id = str(uuid.uuid4())
    s3_key = f"uploads/{user_id}/{image_id}"
    now = int(time.time())

    table.put_item(
        Item={
            "pk": f"USER#{user_id}",
            "sk": f"IMAGE#{image_id}",
            "image_id": image_id,
            "s3_key": s3_key,
            "status": "pending",
            "created_at": now,
        }
    )

    upload_url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket":BUCKET_NAME,
             "Key":s3_key
             },

        ExpiresIn=300
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "image_id" : image_id,
            "s3_key" : s3_key,
            "upload_url": upload_url,
            "status": "pending",
     })
    }