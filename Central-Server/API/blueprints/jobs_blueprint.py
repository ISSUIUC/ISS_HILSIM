import os
import os.path

from apiflask import APIBlueprint
from flask import abort, jsonify, request, Response

import internal.database as database
import internal.auth as auth
import internal.sanitizers as sanitizers
from internal.jobs import *
import util.logs


def sanitize_job_info(job):
    del job["output_path"]
    job["run_status"] = JobStatus(job["run_status"]).name
    return job


jobs_blueprint = APIBlueprint('jobs', __name__)

JOB_OUTPUT_DIR = "output/"
JOB_OUTPUT_PREFIX = JOB_OUTPUT_DIR + "job_"


@jobs_blueprint.route('/jobs', methods=["GET"])
def list_jobs():
    """
    List all the latest 10 jobs

    Additional parameters:
    size: Size of page
    page: the page

    This will return an empty array if there is no available job for that page.
    """
    if not (auth.authenticate_request(request)):
        abort(403)
    # List out all the jobs in the database
    size = request.args.get("size", default=10, type=str)
    page = request.args.get("page", default=0, type=int)
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM hilsim_runs ORDER BY run_status DESC limit %s offset %s",
        (size, page * size))
    # Sort through the json and set status
    structs = database.convert_database_list(cursor, cursor.fetchall())
    structs = [job._asdict() for job in structs]
    for job in structs:
        # Additional formatting
        sanitize_job_info(job)

    return jsonify(structs), 200


@jobs_blueprint.route('/job/<int:job_id>', methods=["GET"])
@jobs_blueprint.output(JobOutSchema())
def job_information(job_id):
    """
    Gets the details of a job
    """
    # Get the jobs data from the job id
    if (auth.authenticate_request(request) == False):
        abort(403)
    # List out all the jobs in the database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hilsim_runs where run_id=%s", (job_id,))
    data = cursor.fetchone()
    if data is None:
        return jsonify({"error": "Job not found"}), 404
    return sanitize_job_info(
        database.convert_database_tuple(
            cursor, data)._asdict())

@jobs_blueprint.route('/job/<int:job_id>/data', methods=["GET"])
def job_data(job_id):
    """
    Gets the results of a job
    """
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
    if os.path.exists(file_name + "/output.txt"):
        try:
            with open(file_name + "/output.txt") as f:
                return Response(str(f.read()), mimetype='text/plain')
        except Exception as e:
            print(f"(/job/id/data) Exception: {e}")
            return "Error with file: " + str(Exception(e)), 500
    else:
        return jsonify({"error": "Output file does not exist"}), 404


@jobs_blueprint.route('/job/<int:job_id>/log', methods=["GET"])
def job_log(job_id):
    """
    Gets the job log for a job
    """
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
    if os.path.exists(file_name + "/kamaji_log.txt"):
        try:
            with open(file_name + "/kamaji_log.txt") as f:
                return Response(str(f.read()), mimetype='text/plain')
        except Exception as e:
            print(f"(/job/id/data) Exception: {e}")
            return "Error with file: " + str(Exception(e)), 500
    else:
        return jsonify({"error": "Log file does not exist"}), 404


@jobs_blueprint.route('/job', methods=["POST"])
@jobs_blueprint.input(JobRequestSchema, location="json")
def queue_job(json_data):
    """
    Adds a job to the queue
    """
    # Queue a job
    if not (auth.authenticate_request(request)):
        abort(403)
        return
    # Sometimes we need to get the form request (such as debugging from postman)
    # Other times we output json
    request_args = json_data

    data_uri = "/api/temp/data"

    if "data_uri" in request_args:
        data_uri = request_args["data_uri"]

    desc = ""
    if "description" in request_args:
        desc = request_args["description"]
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO hilsim_runs (user_id, branch, git_hash, submitted_time, output_path, run_status, description, data_uri) \
                    VALUES (%s, %s, %s, now(), %s || currval ('hilsim_runs_run_id_seq'), %s, %s, %s) RETURNING run_id",
        (request_args['username'],
         request_args['branch'],
         request_args['commit'],
         JOB_OUTPUT_PREFIX,
         0,
         desc,
         data_uri))
    
    

    st = cursor.fetchall()
    conn.commit()
    conn.close()
    cursor.close()

    util.logs.write_to_job_log_timestamp(st[0][0], "Job created successfully")

    if len(st) > 0:
        return jsonify({"status": "Job was created", "run_id": st[0][0]}), 201
    else:
        return jsonify({"error": "Error"}), 400

@jobs_blueprint.route('/temp/data', methods=["GET"])
def get_data():
    """
    Temporary data reader

    TODO: delete this and replace with proper api stuff
    https://github.com/orgs/ISSUIUC/projects/4/views/1?pane=issue&itemId=46405451
    """
    with open("./temp-data/flight_computer.csv") as f:
        lines = f.read()
        return lines
