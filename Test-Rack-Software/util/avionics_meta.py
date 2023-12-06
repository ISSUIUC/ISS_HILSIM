# Class for `platform_meta.py` files.
import os


class PlatformMetaInterface:
    board_type: str = ""
    """What type of avionics stack does this interface work with?"""
    repository_url: str = ""
    """GitHub URL to the repository for this stack"""
    platformio_subdirectory = ""  # Platformio subdirectory (in relation to the repository itself)
    """The subdirectory of the platformio directory, in relation to the repository itself"""

    def __init__(self, file: str) -> None:
        self.remote_path = os.path.join(os.path.dirname(file), './remote')
        """What path should the `remote` folder be in?"""
        self.platformio_path = os.path.join(
            self.remote_path, self.platformio_subdirectory)
        """Platformio path, calculated from remote path"""
