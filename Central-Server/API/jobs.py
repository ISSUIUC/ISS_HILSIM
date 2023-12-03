from flask import Blueprint, render_template, abort,jsonify, request, Response
import database
import auth
import os.path
from enum import Enum
import sanitizers

import os

class JobStatus(Enum):
    QUEUED = 0 # Job is queued and will be run on the next available TARS
    RUNNING = 1 # Job is currently running on TARS
    CANCELED = 2 # Job was canceled by someone #cancelculture
    SUCCESS = 3 # Job was successfully run
    FAILED_CRASHED = 4 # Job crashed on TARS
    FAILED_COMPILE_ERROR = 5 # Job failed to compile
    FAILED_TIMEOUT = 6 # Job timed out, cancelled #cancelculturestrikesagain
    FAILED_OTHER = 7 # Job failed for some other reason
    SETUP = 8

def sanitize_job_info(job):
    del job["output_path"]
    job["run_status"] = JobStatus(job["run_status"]).name
    return job

jobs_blueprint = Blueprint('jobs', __name__)

JOB_OUTPUT_DIR = "output/"
JOB_OUTPUT_PREFIX = JOB_OUTPUT_DIR + "job_"

@jobs_blueprint.route('/jobs', methods=["GET"])
def list_jobs():
    if not (auth.authenticate_request(request)):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hilsim_runs ORDER BY run_id ASC")
    # Sort through the json and set status
    structs = database.convert_database_list(cursor, cursor.fetchall())
    structs = [job._asdict() for job in structs]
    for job in structs:
        # Additional formatting
        sanitize_job_info(job)

    return jsonify(structs), 200

@jobs_blueprint.route('/job/<int:job_id>', methods=["GET"])
def job_information(job_id):
    # Get the jobs data from the job id
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM hilsim_runs where run_id=%s", (job_id,))
    data = cursor.fetchone()
    if data == None:
        return jsonify({"error": "Job not found"})
    return jsonify(sanitize_job_info(database.convert_database_tuple(cursor, data)._asdict())), 200

@jobs_blueprint.route('/job/<int:job_id>/data', methods=["GET"])
def job_data(job_id):
    # Get the jobs data from the job id
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hilsim_runs where run_id=%s", (job_id,))
    data = cursor.fetchone()
    data = database.convert_database_tuple(cursor, data)
    file_name = data.output_path
    if os.path.exists(f"{file_name}"):
        try:
            with open(f"{file_name}") as f:
                return Response(str(f.read()), mimetype='text/csv')
        except Exception as e:
            return "Error with file: " + Exception(e), 500
    else:
        return jsonify({"error": "Output file does not exist"}), 404

@jobs_blueprint.route('/job', methods=["POST"])
def queue_job():
    # Queue a job
    if not (auth.authenticate_request(request)):
        abort(403)
        return
    # Sometimes we need to get the form request (such as debugging from postman)
    # Other times we output json
    request_args = request.form
    if request.content_type == "application/json":
        request_args = request.json

    if "commit" in request_args and "username" in request_args and "branch" in request_args:
        pass
    else:
        return jsonify({"error": "Missing arguments"}), 400

    # Sanitize input
    if (not sanitizers.is_git_hash(request_args["commit"]) or
        not sanitizers.is_github_username(request_args["username"]) or
        not sanitizers.is_branch_name(request_args["branch"])):
        return jsonify({"error": "Invalid arguments"}), 400
    
    data_uri = "/api/temp/data"

    if "data_uri" in request_args:
        data_uri = request_args["data_uri"]

    desc = ""
    if "description" in request_args:
        desc = request_args["description"]
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO hilsim_runs (user_id, branch, git_hash, submitted_time, output_path, run_status, description, data_uri) \
                    VALUES (%s, %s, %s, now(), %s || currval ('hilsim_runs_run_id_seq'), %s, %s, %s) RETURNING run_id",
                   (request_args['username'], request_args['branch'], request_args['commit'], JOB_OUTPUT_PREFIX, 0, desc, data_uri))
    # TODO: Directory will be consructed later when the work actually starts
    st = cursor.fetchall()
    conn.commit()
    conn.close()
    cursor.close()
    if len(st) > 0:
        return jsonify({"status": "Job was created", "run_id": st[0][0]}), 201
    else:
        return jsonify({"error":  "Error"}), 400

# TODO: delete this and replace with proper api stuff
@jobs_blueprint.route('/temp/data', methods=["GET"])
def get_data():
    with open("./temp-data/flight_computer.csv") as f:
        lines = f.read()
        return lines
