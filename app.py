# app.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.after_request
def add_headers(response):
    response.headers['Connection'] = 'close'
    response.headers['Cache-Control'] = 'no-store'
    return response
    
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    return response

@app.route('/')
def home():
    return "🔥 Tunnel is working!"

if __name__ == "__main__":
    app.run(port=5000)
