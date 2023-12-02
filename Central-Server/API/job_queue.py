from flask import Blueprint, render_template, abort,jsonify, request, Response
import database
from enum import Enum
import auth

job_queue_blueprint = Blueprint('job_queue', __name__)
"""
@job_queue_blueprint.route('/list/<string:open_devices>')
def list_open_devices(open_devices):
    if not (auth.authenticate_request(request)):
        abort(403)
    # List the devices and then list if they're available
    return jsonify({"status": open_devices})# Get tars details
"""
