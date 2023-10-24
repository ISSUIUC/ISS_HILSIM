from flask import Blueprint, render_template, abort,jsonify, request, Response
import requests

perms_blueprint = Blueprint('perms', __name__)

#@perms_blueprint.route("/perms", methods=["GET"])
def get_team_membership():
    # TOKEN = request.cookies.get('token')
    url = "https://api.github.com/orgs/ISSUIUC/teams/iss-kamaji-administrators/memberships/mpkarpov-ui"
    x = requests.get(url,
                     headers={'Authorization':"Bearer: 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","Accept": "application/vnd.github+json"})
    
    print(x.content)

get_team_membership()
