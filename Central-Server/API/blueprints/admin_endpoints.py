from apiflask import APIBlueprint
from flask import abort, jsonify, request, Response

import internal.auth as auth
import internal.database as database
import internal.threads as threads

admin_blueprint = APIBlueprint('admin', __name__)

# A reference to the manager thread, imported from main so that we can clear the queue.
main_thread: threads.BoardManagerThread = None
def register_main_thread(mt: threads.BoardManagerThread):
    global main_thread
    main_thread = mt

@admin_blueprint.route('/admin/queue', methods=["DELETE"])
def delete_q():
    global main_thread
    if not (auth.authenticate_request(request)):
        abort(403)

    main_thread.clear_queue() # Clears the program queue of the board manager thread.
    return jsonify({"status": "Success"}), 200

@admin_blueprint.route('/admin/database', methods=["DELETE"])
def delete_db():
    if not (auth.authenticate_request(request)):
        abort(403)

    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hilsim_runs")
    conn.commit()
    return jsonify({"status": "Success"}), 200
