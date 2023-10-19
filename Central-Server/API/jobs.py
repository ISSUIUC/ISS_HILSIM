from flask import Blueprint, render_template, abort,jsonify, request
import database
import auth

jobs_blueprint = Blueprint('jobs', __name__)
@jobs_blueprint.route('/jobs')
def list_jobs():
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hilsim_runs")
    return jsonify(cursor.fetchall())
