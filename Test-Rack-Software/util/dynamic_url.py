import requests

api_source = "https://raw.githubusercontent.com/ISSUIUC/ISS_HILSIM/active_server_url/server_url.txt"
api_default = "http://localhost/"

def get_dynamic_url(kamaji_target="main") -> str:
    """Retrieves the api url for kamaji
    @kamaji_target: Which target to retrieve the URI for? `main` will always be the main Kamaji server."""
    # Read the arguments
    return api_default
    if api_source is not None:
        print("(dynamic url) Retrieving dynamic url")
        result = requests.get(api_source)
        try:
            print("(dynamic url) Successfully retrieved dynamic url " + str(result.content.decode().strip()))
            return result.content.decode().strip()
        except Exception as e:
            print("Failed to retrieve dynamic url:", e)
            return api_default.strip()
    else:
        print("Failed to get dynamic url")
        return api_default.strip()