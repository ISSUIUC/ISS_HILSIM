import util.avionics_meta as AVMeta


class PlatformMeta(AVMeta.PlatformMetaInterface):
    board_type = None
    repository_url = None
    # Platformio subdirectory (in relation to the repository itself)
    platformio_subdirectory = None

    def __init__(self, file: str) -> None:
        super().__init__(file)


meta = PlatformMeta(__file__)
