from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import services.authenticator as authenticator
import json
import traceback
import sys
from waitress import serve
import os

argc = len(sys.argv)
if(argc != 2):
    print("Usage: main.py [environment]")
    exit(1)


app = Flask(__name__)
CORS(app)

@app.route("/")
def api_index():
    return "OK"


@app.route("/authenticate", methods=["POST"])
def authenticate_github_user():
    try:
        status, access_token = authenticator.get_user_access_token(request.json['github_code'])
        if(status == 'ok'):
            return access_token, 200
        else:
            return access_token, 500
    except:
        error_msg = traceback.format_exc(4)
        return "Unable to retrieve github code from request\n\n" + error_msg, 400

if __name__ == "__main__":
    
    port = int(os.environ.get('PORT', 443))
    print("PORT:", port)
    if(sys.argv[1] == "dev"):
        print("Initialized development websocket server on ws://localhost:" + str(port))
        socketio = SocketIO(app, cors_allowed_origins='*')
        app.run(debug=True, host="0.0.0.0", port=port)
        socketio.run()
    else:
        print("Initialized production API on http://localhost:" + str(port))
        print("Initialized production websocket server on ws://localhost:" + str(port))
        socketio = SocketIO(app)
        serve(app, port=port)
        
