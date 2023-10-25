from flask import Blueprint, render_template, abort,jsonify, request, Response
import requests


perms_blueprint = Blueprint('perms', __name__)

#@perms_blueprint.route("/perms", methods=["GET"])
def get_team_membership():
    # TOKEN = request.cookies.get('token')
    url = "https://api.github.com/orgs/ISSUIUC/teams/iss-kamaji-administrators/memberships/mpkarpov-ui"
    x = requests.get(url=url,
                     headers={"Accept": "application/vnd.github+json", 'Authorization':"Bearer <ACCESS CODE>", "Content-Type": "text/html; charset=utf-8", "X-GitHub-Api-Version":"2022-11-28"})
    
    print(x)
    print(x.content)

get_team_membership()
