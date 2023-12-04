from flask import Flask, jsonify, Response
from flask_socketio import SocketIO
import sys
from waitress import serve
import os
import internal.database as database
from blueprints.jobs_blueprint import jobs_blueprint
import random
from job_queue import job_queue_blueprint
from blueprints.perms import perms_blueprint
import threading
import util.communication.packets as packets
from apiflask import APIFlask
import internal.boards
import argparse

from flask_cors import CORS

from internal.threads import BoardManagerThread


parser = argparse.ArgumentParser()
parser.add_argument("runmode", help="Enter the mode you want to run in: dev or prod", type=str)
args = parser.parse_args()


app = APIFlask(__name__, title="Kamaji", static_url_path="/static", static_folder="./static")
app.register_blueprint(jobs_blueprint)
app.register_blueprint(job_queue_blueprint)
app.register_blueprint(perms_blueprint)
CORS(app)
m_thread = BoardManagerThread()

app.config['SPEC_FORMAT'] = 'json'
app.config['SERVERS'] = [
    {
        'name': 'Dev Server',
        'url': 'http://localhost/api/'
    }
    # TODO: Add prod
]

@app.route("/")
def api_index():
    return "OK"

@app.errorhandler(403)
def access_forbidden_error(e):
    if random.randint(0, 100000) == 42069: # We are a really serious space program, check out the CEO of SpaceX, we like the same jokes
        return "<html><h1>Access forbidden :(</h1><img src=\"/api/static/image_480.png\"/></html>", 200
    return jsonify(error=str(e)), 403

def generate_jobs_table():
    # Generate database if it doesn't exist
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_tables WHERE tablename='hilsim_runs'")
    exists = cursor.fetchone()
    if not exists:
        with open("database.sql") as f:
            cursor.execute(f.read())
        conn.commit()
        conn.close()
        cursor.close()

@app.route('/boards', methods=["GET"])
@app.output(internal.boards.BoardList())
def list_boards():
    """
    List all the boards that are connected to the server
    """
    board_list = []
    for board in m_thread.threads:
        board_list.append({
            "id": board.board_id,
            "is_ready": board.is_ready,
            "job_running": board.job_running,
            "board_type": board.board_type,
            "running": board.running
        })
    return {
        "boards": board_list
    }, 200

@app.route('/internal/queue', methods=["GET"])
def list_internal_queue():
    """
    Debug function to index the size of the current queue
    """
    return jsonify({"size": len(m_thread.queue), "content": [str(e) for e in m_thread.queue]}), 200

if __name__ == "__main__":
    print("Attempting to initialize server..")
    jobs = []

    file = open(os.path.join(os.path.dirname(__file__), "./util/datastreamer_test_data.csv"), 'r')
    csv_data = file.read()

    m_thread.start()

    generate_jobs_table()

    port = int(os.environ.get('PORT', 443))
    print("PORT:", port)
    if(args.runmode=="dev"):
        print("Initialized development websocket server on ws://localhost:" + str(port))
        socketio = SocketIO(app, cors_allowed_origins='*')
        app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
        socketio.run()
    else:
        print("Initialized production API on http://localhost:" + str(port))
        print("Initialized production websocket server on ws://localhost:" + str(port))
        socketio = SocketIO(app)
        serve(app, port=port)
