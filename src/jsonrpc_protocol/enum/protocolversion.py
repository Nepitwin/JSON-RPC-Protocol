from enum import Enum


class ProtocolVersion(Enum):
    v1 = "1.0"
    v2 = "2.0"

    @staticmethod
    def from_str(version):
        if version in "1.0":
            return ProtocolVersion.v1
        elif version in "2.0":
            return ProtocolVersion.v2
        else:
            raise NotImplementedError
