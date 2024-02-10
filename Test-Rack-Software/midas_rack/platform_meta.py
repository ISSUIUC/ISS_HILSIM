import util.avionics_meta as AVMeta


class PlatformMeta(AVMeta.PlatformMetaInterface):
    board_type = "MIDASmkI"
    repository_url = "https://github.com/ISSUIUC/MIDAS-Software.git"
    default_branch = "main"
    # Platformio subdirectory (in relation to the repository itself)
    platformio_subdirectory = "./MIDAS"
    kamaji_target = "main"

    def __init__(self, file: str) -> None:
        super().__init__(file)


meta = PlatformMeta(__file__)