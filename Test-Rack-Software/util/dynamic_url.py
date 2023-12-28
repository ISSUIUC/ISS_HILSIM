import requests

api_source = "https://jsonblob.com/api/jsonBlob/1182790336216162304"
api_default = "http://localhost"

def get_dynamic_url(kamaji_target="main") -> str:
    """Retrieves the api url for kamaji
    @kamaji_target: Which target to retrieve the URI for? `main` will always be the main Kamaji server."""
    if api_source is not None:
        result = requests.get(api_source)
        try:
            json = result.json()
            return json[kamaji_target]
        except Exception as e:
            print("Failed to retrieve dynamic url:", e)
            return api_default
    else:
        print("Failed to get dynamic url")
        return api_default