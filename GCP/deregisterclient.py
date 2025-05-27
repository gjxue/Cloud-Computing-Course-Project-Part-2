from google.cloud import firestore
import functions_framework
from flask import request, jsonify

db = firestore.Client()
COLLECTION = "webhook_clients"

@functions_framework.http
def deregister_client(request):
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return "Missing 'url'", 400

        docs = db.collection(COLLECTION).where("url", "==", url).stream()

        deleted = 0
        for doc in docs:
            db.collection(COLLECTION).document(doc.id).delete()
            deleted += 1
            break  # Delete only the first match

        if deleted == 0:
            return jsonify({"message": "URL not found"}), 404
        else:
            return jsonify({"message": "URL deregistered"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500