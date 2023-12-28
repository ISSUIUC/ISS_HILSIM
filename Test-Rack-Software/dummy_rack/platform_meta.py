import util.avionics_meta as AVMeta


class PlatformMeta(AVMeta.PlatformMetaInterface):
    board_type = "DUMMY"
    repository_url = ""
    default_branch = ""
    # Platformio subdirectory (in relation to the repository itself)
    platformio_subdirectory = ""
    kamaji_target = "test"

    def __init__(self, file: str) -> None:
        super().__init__(file)


meta = PlatformMeta(__file__)
