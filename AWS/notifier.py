import boto3
import requests
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info("Lambda triggered. Event payload:")
        logger.info(json.dumps(event))

        # Extract bucket and key from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        logger.info(f"S3 bucket: {bucket}")
        logger.info(f"S3 object key: {key}")

        # Generate a signed URL for the object
        s3 = boto3.client('s3')
        signed_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600
        )
        logger.info("Generated signed S3 URL:")
        logger.info(signed_url)

        # Call the Azure Function with the signed URL
        azure_url = 'https://wngsr-extractor.azurewebsites.net/api/extract'
        logger.info(f"Calling Azure Function: {azure_url}")

        response = requests.get(azure_url, params={'csv_url': signed_url})
        logger.info(f"Azure Function responded with status code {response.status_code}")
        logger.info(f"Response body: {response.text}")

        return {
            'statusCode': response.status_code,
            'body': response.text
        }

    except Exception as e:
        logger.error("An error occurred:", exc_info=True)
        return {
            'statusCode': 500,
            'body': f"Error calling Azure Function: {str(e)}"
        }