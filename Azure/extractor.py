import azure.functions as func
import logging
import urllib.request
import json
import csv
import io

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="extract")
def extract(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing CSV extraction request.')

    csv_url = req.params.get('csv_url')
    if not csv_url:
        return func.HttpResponse("Missing 'csv_url' query parameter.", status_code=400)

    try:
        with urllib.request.urlopen(csv_url) as response:
            csv_content = response.read().decode('utf-8')
    except Exception as e:
        logging.error(f"Error downloading CSV: {e}")
        return func.HttpResponse(f"Failed to download or parse CSV: {e}", status_code=500)

    # Use csv.reader for proper comma and quote handling
    csv_reader = csv.reader(io.StringIO(csv_content))
    total_storage = None

    for row in csv_reader:
        if row and row[0].strip() == "Total":
            logging.info(f"Parsed Total row: {row}")
            if len(row) > 1:
                total_storage = row[1].strip()
            break

    if total_storage is None:
        return func.HttpResponse(
            "Could not extract total storage from Total row.",
            status_code=422
        )

    result = {
        "total_storage": total_storage
    }

    relay_url = 'https://relaypayload-405685547993.us-east1.run.app'
    try:
        data_bytes = json.dumps(result).encode('utf-8')
        req = urllib.request.Request(
            url=relay_url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as resp:
            logging.info(f"Successfully pushed to GCP relay: {resp.status} {resp.reason}")
    except Exception as e:
        logging.error(f"Push to GCP relay failed: {e}")
        return func.HttpResponse(f"Push to GCP relay failed: {e}", status_code=502)

    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200
    )