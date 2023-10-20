from flask import Blueprint, render_template, abort,jsonify, request, Response
import database
import auth
import os.path
from enum import Enum
import sanitizers

class JobStatus(Enum):
    QUEUED = 0 # Job is queued and will be run on the next available TARS
    RUNNING = 1 # Job is currently running on TARS
    CANCELLED = 2 # Job was cancelled by someone #cancelculture
    SUCCESS = 3 # Job was successfully run
    FAILED_CRASHED = 4 # Job crashed on TARS
    FAILED_COMPILE_ERROR = 5 # Job failed to compile
    FAILED_TIMEOUT = 6 # Job timed out, cancelled #cancelculturestrikesagain
    FAILED_OTHER = 7 # Job failed for some other reason

def convert_job_info(job):
    if job[8] > 7 or job[8] < 0:
        job[8] = 7

    return {"id": job[0],
          "username": job[1],
          "branch": job[2],
          "hash": job[3],
          "date_queue": job[5],
          "date_start": job[6],
          "date_end": job[7],
          "status": JobStatus(job[8]).name,
          }

jobs_blueprint = Blueprint('jobs', __name__)
@jobs_blueprint.route('/jobs/list')
def list_jobs():
    if not (auth.authenticate_request(request)):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hilsim_runs")
    # Sort through the json and set status
    job_list = []
    for job in cursor.fetchall():
        job_list.append(convert_job_info(job))
    return jsonify(job_list)

@jobs_blueprint.route('/jobs/<int:job_id>')
def job_information(job_id):
    # Get the jobs data from the job id
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM hilsim_runs where run_id={job_id}")
    data = cursor.fetchone()

    return jsonify(data)

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

@jobs_blueprint.route('/jobs/queue', methods=["GET"])
def queue_job():
    # Queue a job
    if not (auth.authenticate_request(request)):
        abort(403)
    if "commit" in request.args and "username" in request.args and "branch" in request.args:
        pass
    else:
        return jsonify({"status": "Missing arguments"}), 400
    # Sanitize input
    if not sanitizers.is_hex(request.args["commit"]) or not sanitizers.is_github_username(request.args["username"]) or not sanitizers.is_alphanum(request.args["branch"]):
        return jsonify({"status": "Invalid arguments"}), 400
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO hilsim_runs (user_id, branch, git_hash, submitted_time, output_path, run_status) VALUES ('{request.args['username']}', '{request.args['branch']}', '{request.args['commit']}', now(), 'output.csv', 0)")
    conn.commit()
    conn.close()
    cursor.close()
    return jsonify({"status": "Ok"}), 200
