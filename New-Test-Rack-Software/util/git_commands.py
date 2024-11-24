import requests
from dotenv import load_dotenv

import os

def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def download_artifact():
    env_file_path = "../../.env"
    load_dotenv(dotenv_path=env_file_path)

    github_token = os.getenv("GITHUB_TOKEN")

    url = "https://api.github.com/repos/ISSUIUC/MIDAS-Software/actions/artifacts/2198515330/zip"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(url, headers=headers, allow_redirects=False)
    artifact_url = response.headers['Location']

    download_url(artifact_url, "./file.zip")

download_artifact()