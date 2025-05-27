from google.cloud import firestore
import functions_framework
from flask import jsonify, request

db = firestore.Client()
COLLECTION = "webhook_clients"

@functions_framework.http
def register_client(request):
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return "Missing 'url'", 400

        doc_ref = db.collection(COLLECTION).add({"url": url})
        return jsonify({"message": "Registered", "id": doc_ref[1].id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500