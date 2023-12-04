"""This file will eventually contain all the functions necessary to determine who a user is and what they can do."""
def authenticate_request(xhr) -> bool:
    """Determine if the request has MEMBER-status permission (user is a member of ISSUIUC)"""
    return True # TODO: actual checks
