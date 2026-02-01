from bbc_server.packages import BasePackage

class StatusUpdatePackage(BasePackage):
    PACKAGE_TYPE = "status-update"
    JSON_PARAM_MAP = {
        "is-ready": "is_ready"
    }

    def __init__(self, is_ready: bool):
        """StatusUpdatePackage
        see the package documentation for more information

        Args:
            is_ready (bool): readiness status
        """
        self.__is_ready = is_ready

    def _generate_body_dict(self) -> dict:
        return {"is-ready": self.__is_ready}

    @property
    def is_ready(self) -> bool:
        return self.__is_ready

    def __repr__(self):
        return f"StatusUpdatePackage({self.is_ready})"
