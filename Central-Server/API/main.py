"""
  _  __                     _ _
 | |/ /                    (_|_)
 | ' / __ _ _ __ ___   __ _ _ _
 |  < / _` | '_ ` _ \\ / _` | | |
 | . \\ (_| | | | | | | (_| | | |
 |_|\\_\\__,_|_| |_| |_|\\__,_| |_|
                          _/ |
                         |__/
 ILLINOIS SPACE SOCIETY -- KAMAJI

This is the entrypoint for the Kamaji service, designed by the Kamaji team in 2023:
Michael Karpov (2027)
Zyun Lam (2027)
Surag Nuthulapaty (2027)
Carson Sprague (2025)
Deeya Bodas (2025)
Anthony Smykalov (2025)

Under oversight of
Aidan Costello (2026)
Peter Giannetos (2025)

------------------------------------------------------------------------------

Kamaji was developed with the express goal of making avionics development and testing a more streamlined process across Spaceshot.
The documentation for this specific service is held within this directory's README.md file. This entrypoint file can be run as a standalone
with { python ./main.py [dev/prod] }, or with the entire service by running the compose.prod.yml or compose.yml files as docker-compose instructions
in the root of this repository.
"""

import sys
import os
import random
import argparse
import logging

from flask import Flask, jsonify, Response
from flask_socketio import SocketIO
from waitress import serve
from blueprints.jobs_blueprint import jobs_blueprint
from blueprints.perms import perms_blueprint
from blueprints.admin_endpoints import admin_blueprint, register_main_thread
from apiflask import APIFlask
from flask_cors import CORS

import internal.boards
import internal.database as database
from internal.threads import BoardManagerThread

# Handle main.py command line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "runmode",
    help="Enter the mode you want to run in: dev or prod",
    type=str)
args = parser.parse_args()

# Initialize the API
app = APIFlask(
    __name__,
    title="Kamaji",
    static_url_path="/static",
    static_folder="./static")
app.register_blueprint(jobs_blueprint)
app.register_blueprint(perms_blueprint)
app.register_blueprint(admin_blueprint)
CORS(app)

print("(CORS) enabled CORS logging")
logging.getLogger('flask_cors').level = logging.DEBUG

# Initialize datastreamer connectiosn
m_thread = BoardManagerThread()
register_main_thread(m_thread)

# Set up server configs
app.config['SPEC_FORMAT'] = 'json'
app.config['SERVERS'] = [
    {
        'name': 'Dev Server',
        'url': 'http://localhost/api/'
    }
    # TODO: Add prod
]

# Set up API endpoints


@app.route("/")
def api_index():
    """/api/ -- Returns literal 'OK'"""
    return "OK"


@app.errorhandler(403)
def access_forbidden_error(e):
    """err 403 -- Returns normal 403 error"""
    if random.randint(
            0,
            100000) == 42069:  # We are a really serious space program, check out the CEO of SpaceX, we like the same jokes
        return "<html><h1>Access forbidden :(</h1><img src=\"/api/static/image_480.png\"/></html>", 200
    return jsonify(error=str(e)), 403


@app.route('/boards', methods=["GET"])
@app.output(internal.boards.BoardList())
def list_boards():
    """
    /api/boards/ -- List all the boards that are connected to the server
    """
    board_list = []
    for board in m_thread.threads:
        board_list.append({
            "id": board.board_id,
            "is_ready": board.flags.is_ready,
            "job_running": board.flags.job_running,
            "board_type": board.board_type,
            "running": board.running
        })
    return {
        "boards": board_list
    }, 200


@app.route('/internal/queue', methods=["GET"])
def list_internal_queue():
    """
    /api/internal/queue -- Debug function to index the size of the current queue
    """
    return jsonify({"size": len(m_thread.queue), "content": [
                   str(e) for e in m_thread.queue]}), 200


if __name__ == "__main__":
    # Perform final initialization
    print("Attempting to initialize server..")
    jobs = []

    # Start the running of manager thread
    m_thread.start()

    # Re-initialize database
    database.generate_jobs_table()

    port = int(os.environ.get('PORT', 443))
    print("PORT:", port)
    if (args.runmode == "dev"):
        # Init dev server
        print(
            "Initialized development websocket server on ws://localhost:" +
            str(port))
        socketio = SocketIO(app, cors_allowed_origins='*')
        app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
        socketio.run()
    elif (args.runmode == "prod"):
        # Init prod server
        print("Initialized production API on http://localhost:" + str(port))
        print(
            "Initialized production websocket server on ws://localhost:" +
            str(port))
        socketio = SocketIO(app)
        serve(app, port=port)
    else:
        raise ValueError("An invalid runmode was used. The only options are dev/prod")
