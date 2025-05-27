import urllib.request
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # CSV source
    url = "https://ir.eia.gov/ngs/wngsr.csv"
    response = urllib.request.urlopen(url)
    csv_data = response.read()
    
    # Generate filename using current UTC date
    now = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"wngsr_{now}.csv"
    
    # Upload to S3
    s3 = boto3.client('s3')
    bucket_name = "wngsr-csv-storage"  # 🔁 Update to your actual bucket
    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=csv_data
    )
    
    return {
        'statusCode': 200,
        'body': f"File {filename} uploaded to {bucket_name}"
    }