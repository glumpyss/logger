# ip_logger_app.py
from flask import Flask, request, redirect, jsonify
import requests
import json
import os

app = Flask(__name__)

# --- Configuration ---
# IMPORTANT: Replace this with your actual Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1382611407199014912/A6GHc65WzrRbciHynuMssat9MI0eYlONJTq3sinrx5TtmjGpCFtc7qCwlfirzh_qxfPd"

# The default URL to redirect to if 'url' parameter is not provided
# This is your game URL that you want to track clicks for.
DEFAULT_REDIRECT_URL = "https://game.up.railway.app"

# --- Helper Functions ---
def get_client_ip():
    """
    Attempts to get the client's real IP address, considering common proxy headers.
    Order of preference: X-Forwarded-For, X-Real-IP, then Flask's request.remote_addr.
    """
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain a comma-separated list of IPs.
        # The client's IP is usually the first one.
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP').strip()
    else:
        return request.remote_addr

def send_discord_webhook(ip_address, redirect_target):
    """
    Sends an embed message to the configured Discord webhook URL.
    """
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL is not set.")
        return

    embed = {
        "title": "Link Clicked - IP Logged!",
        "description": f"A user clicked your tracking link.",
        "color": 3066993,  # Green color for the embed
        "fields": [
            {
                "name": "Clicked IP Address",
                "value": f"```{ip_address}```", # Display IP in a code block
                "inline": False
            },
            {
                "name": "Redirected To",
                "value": f"[Railway Game App]({redirect_target})",
                "inline": False
            }
        ],
        "footer": {
            "text": "IP Logger by Gemini"
        },
        "timestamp": requests.utils.datetime.datetime.now().isoformat()
    }

    payload = {
        "embeds": [embed]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully sent IP '{ip_address}' to Discord webhook.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord webhook: {e}")
        # Log the full response for debugging Discord issues
        if hasattr(e, 'response') and e.response is not None:
            print(f"Discord API Response Status: {e.response.status_code}")
            print(f"Discord API Response Body: {e.response.text}")


# --- Flask Routes ---
@app.route('/track')
def track_click():
    """
    This endpoint captures the IP, sends it to Discord, and then redirects.
    Usage: https://your-server.com/track?url=https://game.up.railway.app
    If 'url' parameter is not provided, it redirects to DEFAULT_REDIRECT_URL.
    """
    client_ip = get_client_ip()
    target_url = request.args.get('url', DEFAULT_REDIRECT_URL)

    print(f"Received click from IP: {client_ip}. Redirecting to: {target_url}")

    # Send the IP to Discord webhook
    send_discord_webhook(client_ip, target_url)

    # Redirect the user to the target URL
    return redirect(target_url, code=302) # Use 302 for temporary redirect

@app.route('/')
def home():
    """
    Simple home page for the tracking service.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IP Tracker & Redirector</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body { font-family: 'Inter', sans-serif; }
        </style>
    </head>
    <body class="bg-gray-100 flex items-center justify-center min-h-screen p-4">
        <div class="bg-white p-8 rounded-lg shadow-md text-center max-w-md w-full">
            <h1 class="text-2xl font-bold mb-4 text-gray-800">IP Tracker & Redirector Service</h1>
            <p class="text-gray-600 mb-6">
                This service captures IP addresses when a link is clicked and sends them to a Discord webhook,
                then redirects the user to the intended destination.
            </p>
            <p class="text-gray-700 font-semibold">
                To use, share a link like this:
            </p>
            <pre class="bg-gray-100 p-3 rounded text-sm text-left overflow-x-auto my-4 border border-gray-300">
                <code class="text-blue-700">https://<span class="font-bold">YOUR_SERVER_DOMAIN</span>/track?url=https://game.up.railway.app</code>
            </pre>
            <p class="text-xs text-gray-500">
                Replace <span class="font-bold">YOUR_SERVER_DOMAIN</span> with the domain where you deploy this Flask app.
            </p>
            <p class="mt-6 text-sm text-gray-500">
                This is a backend service. No direct interaction needed here.
            </p>
        </div>
    </body>
    </html>
    """

# --- Run the App ---
if __name__ == '__main__':
    # Use Gunicorn or a production WSGI server for actual deployment.
    # For local testing:
    # app.run(debug=True, host='0.0.0.0', port=5000)
    print("To run this Flask app in production, use a WSGI server like Gunicorn.")
    print("Example: gunicorn -w 4 'ip_logger_app:app'")
    print("For local development, uncomment app.run(debug=True, ...) line.")
