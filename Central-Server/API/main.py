from flask import Flask, jsonify
from flask_socketio import SocketIO
import sys
from waitress import serve

argc = len(sys.argv)
if(argc != 2):
    print("Usage: main.py [environment]")
    exit(1)


app = Flask(__name__)

@app.route("/")
def api_index():
    return "OK"


@app.route("/get-list", methods=["GET"])
def get_generic():
    return jsonify([1,3,5,100])

if __name__ == "__main__":
    if(sys.argv[1] == "dev"):
        print("Initialized development websocket server on ws://localhost:433")
        socketio = SocketIO(app, cors_allowed_origins='*')
        app.run(debug=True, port=443)
        socketio.run()
    else:
        socketio = SocketIO(app)
        print("Initialized production API on http://localhost:433")
        print("Initialized production websocket server on ws://localhost:433")
        serve(app, port=443)
        
