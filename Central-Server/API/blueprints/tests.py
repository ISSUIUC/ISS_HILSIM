# Blueprint file for tests to be run (used to emulate user requests.)

from apiflask import APIBlueprint
from flask import render_template, abort, jsonify, request, Response
import requests
import os

tests_blueprint = APIBlueprint('tests', __name__)

@tests_blueprint.route("/tests/", methods=["GET"])
def can_run_tests():
    """Determine if tests can be run"""
    # Determine if testing is enabled
    try:
        if (not os.environ['USE_TESTING_ENVIRONMENT']):
            abort(503)
            return
    except:
        abort(503)
        return
    return "TESTS OK"

@tests_blueprint.route("/tests/datastreamer-comp", methods=["GET"])
def datastreamer_comp_test():
    """Comprehensive tests for Datastreamer"""
    # Determine if testing is enabled
    try:
        if (not os.environ['USE_TESTING_ENVIRONMENT']):
            abort(503)
            return
    except:
        abort(503)
        return
    
    # Tests can run
