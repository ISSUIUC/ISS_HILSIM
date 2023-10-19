from flask import Blueprint, render_template, abort,jsonify, request, Response
import database
from enum import Enum
import auth

job_queue_blueprint = Blueprint('job_queue', __name__)
@job_queue_blueprint.route('/list')
def list_open_tars():
    if not (auth.authenticate_request(request)):
        abort(403)
    return jsonify({"status": "Tars should be available, I think"})# Get tars details
