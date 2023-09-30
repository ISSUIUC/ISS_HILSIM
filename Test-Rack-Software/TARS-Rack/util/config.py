import os

board_type = "TARS"

repository_url = "https://github.com/ISSUIUC/TARS-Software.git"
platformio_subdirectory = "./TARS" # Platformio subdirectory (in relation to the repository itself)

remote_path = os.path.join(os.path.dirname(__file__), "../remote")
platformio_path = os.path.join(remote_path, platformio_subdirectory)