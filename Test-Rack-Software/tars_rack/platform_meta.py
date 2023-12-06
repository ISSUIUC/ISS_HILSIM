import util.avionics_meta as AVMeta


class PlatformMeta(AVMeta.PlatformMetaInterface):
    board_type = "TARSmkIV"
    repository_url = "https://github.com/ISSUIUC/TARS-Software.git"
    # Platformio subdirectory (in relation to the repository itself)
    platformio_subdirectory = "./TARS"

    def __init__(self, file: str) -> None:
        super().__init__(file)


meta = PlatformMeta(__file__)
