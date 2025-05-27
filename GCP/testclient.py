import functions_framework
from flask import request

@functions_framework.http
def client_receiver(request):
    payload = request.get_data(as_text=True)
    print(f"🔔 Received payload: {payload}")
    return f"Received payload: {payload}", 200