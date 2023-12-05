"""This file will eventually contain all the functions necessary to determine who a user is and what they can do."""
from flask import Request

def authenticate_request(xhr: Request) -> bool:
    """Determine if the request has MEMBER-status permission (user is a member of ISSUIUC)"""
    return True # TODO: actual checks
