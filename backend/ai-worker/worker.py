import os
import time
import json
import io
from PIL import Image
import urllib.parse
import boto3
import numpy as np
import onnxruntime as ort
from pathlib import Path


TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")


# Load model and classes at startup, can be reused for warm starts
BASE_DIR = Path(__file__).resolve().parent
CLASSES = json.loads((BASE_DIR / "classes.json").read_text())
SESSION = ort.InferenceSession(str(BASE_DIR / "sharingan_ai.onnx"))

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
CONFIDENCE_THRESHOLD = 0.80


# preparing image for model
def preprocess(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255
    arr = (arr-MEAN)/STD
    return arr.transpose(2,0,1) [None, ...]


# convert logits to percentage
def softmax(logits):
    exp = np.exp(logits - np.max(logits))
    return exp / exp.sum()


# predicting character
def predict_character(image_bytes):
    input_image = preprocess(image_bytes)
    logits = SESSION.run(None, {"input": input_image})[0][0]
    probabilities = softmax(logits)

    best_guess_idx = int(np.argmax(probabilities))
    confidence = float(probabilities[best_guess_idx])
    predicted = CLASSES[best_guess_idx]

    if confidence < CONFIDENCE_THRESHOLD or predicted == "other_unknown":
        return "Unknown", confidence
    
    return predicted, confidence



def lambda_handler(event,context):

    for record in event.get("Records",[]):
        bucket_name = record["s3"]["bucket"]["name"]
        raw_key = record["s3"]["object"]["key"]
        s3_key = urllib.parse.unquote_plus(raw_key)

        print(f"Processing file: {s3_key}")

        parts = s3_key.split("/")
        if len(parts) !=3:
            print(f"Skipping wrong path: {s3_key}")
            continue

        _, user_id, image_id = parts

        resource = s3.get_object(Bucket=bucket_name, Key=s3_key)
        image_bytes = resource["Body"].read()

        character_name, confidence = predict_character(image_bytes)
        print(f"Prediction: {character_name} ({confidence * 100:.1f}%)")

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
                ":char": character_name,
                ":now" : int(time.time())
            }
        )
        print(f"Updated image {s3_key} is complete")

    return {
    "statusCode":200,
    "status":"success",
    }
