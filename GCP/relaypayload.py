from google.cloud import firestore
import functions_framework
from flask import request, jsonify
import requests

db = firestore.Client()
COLLECTION = "webhook_clients"

@functions_framework.http
def relay_payload(request):
    try:
        payload = request.get_data(as_text=True)

        docs = db.collection(COLLECTION).stream()
        urls = [doc.to_dict().get("url") for doc in docs if doc.exists]

        successes = 0
        for url in urls:
            try:
                res = requests.post(url, data=payload, headers={'Content-Type': 'text/plain'})
                print(f"Pushed to {url}: {res.status_code}")
                successes += 1
            except Exception as e:
                print(f"Failed to push to {url}: {e}")

        return jsonify({"status": "pushed", "clients": successes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500