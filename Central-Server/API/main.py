from flask import Flask, jsonify, Response
from flask_socketio import SocketIO
import sys
from waitress import serve
import os
import database
from jobs import jobs_blueprint
import random
from job_queue import job_queue_blueprint
from perms import perms_blueprint
import threading
import util.communication.packets as packets
from flask_cors import CORS

from threads import manager_thread

argc = len(sys.argv)
if(argc != 2):
    print("Usage: main.py [environment]")
    exit(1)

app = Flask(__name__, static_url_path="/static", static_folder="./static")
app.register_blueprint(jobs_blueprint)
app.register_blueprint(job_queue_blueprint)
app.register_blueprint(perms_blueprint)
CORS(app)
m_thread = manager_thread()

@app.route("/")
def api_index():
    return "OK"

@app.errorhandler(403)
def access_forbidden_error(e):
    if random.randint(0, 100000) == 42069: # We are a really serious space program, check out the CEO of SpaceX, we like the same jokes
        return "<html><h1>Access forbidden :(</h1><img src=\"/api/static/image_480.png\"/></html>", 200
    return jsonify(error=str(e)), 403

@app.route("/generate_database", methods=["GET"])
def generate_jobs_table():
    conn = database.connect()
    cursor = conn.cursor()
    try:
        with open("database.sql") as f:
            cursor.execute(f.read())
        conn.commit()
        conn.close()
        cursor.close()
        return "Ok", 200
    except Exception as e:
        return Response("Not Ok: " + str(e), 500)

@app.route('/list/')
def list_boards():
    board_list = []
    for board in m_thread.threads:
        board_list.append({
            "id": board.board_id,
            "is_ready": board.is_ready,
            "job_running": board.job_running,
            "board_type": board.board_type,
            "running": board.running
        })
    return jsonify(board_list), 200

if __name__ == "__main__":
    print("Attempting to initialize server..")
    # m_thread = threading.Thread(target=manager_thread)
    jobs = []

    file = open(os.path.join(os.path.dirname(__file__), "./util/datastreamer_test_data.csv"), 'r')
    csv_data = file.read()

    m_thread.start()

    port = int(os.environ.get('PORT', 443))
    print("PORT:", port)
    if(sys.argv[1] == "dev"):
        print("Initialized development websocket server on ws://localhost:" + str(port))
        socketio = SocketIO(app, cors_allowed_origins='*')
        app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
        socketio.run()
    else:
        print("Initialized production API on http://localhost:" + str(port))
        print("Initialized production websocket server on ws://localhost:" + str(port))
        socketio = SocketIO(app)
        serve(app, port=port)
