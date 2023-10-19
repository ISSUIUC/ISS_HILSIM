from flask import Flask, jsonify
from flask_socketio import SocketIO
import sys
from waitress import serve
import os
import psycopg2

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

@app.route("/ping", methods=["GET"])
def ping():
    conn = psycopg2.connect(database="postgres",
                    host="db",
                    user="postgres",
                    password="example",
                    port=5432)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ping")
    web = cursor.fetchone()
    st = "<h1 style=\"font-size:108\">" + str(web[1]) + "</h1>"
    return st

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
        
