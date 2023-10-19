from flask import Blueprint, render_template, abort,jsonify, request, Response
import database
import auth
import os.path

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

@jobs_blueprint.route('/jobs/<int:job_id>')
def job_information(job_id):
    # Get the jobs data from the job id
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM hilsim_runs where run_id={job_id}")
    return jsonify(cursor.fetchone())

@jobs_blueprint.route('/jobs/data/<int:job_id>')
def job_data(job_id):
    # Get the jobs data from the job id
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM hilsim_runs where run_id={job_id}")
    data = cursor.fetchone()
    file_name = data[4]
    if os.path.exists(f"{file_name}"):
        try:
            with open(f"{file_name}") as f:
                return Response(str(f.read()), mimetype='text/csv')
        except Exception as e:
            return "Error with file: " + Exception(e), 500
    else:
        return file_name + " does not exist", 404
