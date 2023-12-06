from apiflask import APIBlueprint
from flask import render_template, abort, jsonify, request, Response
import requests


perms_blueprint = APIBlueprint('perms', __name__)


@perms_blueprint.route("/perms/<string:username>", methods=["GET"])
def get_team_membership(username):
    TOKEN = request.cookies.get('token')
    # TOKEN = ''
    url = f"https://api.github.com/orgs/ISSUIUC/teams/iss-kamaji-administrators/memberships/{username}"
    x = requests.get(
        url=url,
        headers={
            "Accept": "application/vnd.github+json",
            'Authorization': f"Bearer {TOKEN}",
            "Content-Type": "text/html; charset=utf-8",
            "X-GitHub-Api-Version": "2022-11-28"})

    return x.status_code == 200
