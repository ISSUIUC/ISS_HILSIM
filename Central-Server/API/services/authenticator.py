import requests
import os
from urllib.parse import parse_qs, urlparse
import urllib.parse
from dotenv import dotenv_values

github_auth = dotenv_values(".env")

def get_user_access_token(github_code: str):
    uri = "https://github.com/login/oauth/access_token/"
    data = {
        'client_id': github_auth['REACT_APP_GITHUB_CLIENT_ID'],
        'client_secret': github_auth['REACT_APP_GITHUB_CLIENT_SECRET'],
        'code': github_code
    }

    response = requests.post(uri, data)
    parsed_dict = parse_qs(urllib.parse.unquote(response.text))
    if('error' in parsed_dict):
        return 'error', parsed_dict
    else:
        return 'ok', parsed_dict
