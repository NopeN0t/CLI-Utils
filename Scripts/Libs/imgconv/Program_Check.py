from dataclasses import dataclass
from enum import Enum

from Colors.ConsoleColors import ConsoleColors as CC
from Functions.Checkers import Custom_Checker, exiftool_Check #exiftool_check is there for external import


@dataclass(frozen=True)
class Support:
    program: str
    command: tuple[str, ...]
    exit_on_failure: bool
    message: str

    def check(self):
        return Custom_Checker(
            self.program,
            list(self.command),
            self.exit_on_failure,
            self.message,
        )


class Supports(Enum):
    JXL = Support(
        "cjxl",
        ("cjxl", "-V"),
        False,
        f"{CC.ERROR}cjxl.exe not found{CC.RESET}",
    )

    WEBP = Support(
        "cwebp",
        ("cwebp", "-version"),
        False,
        f"{CC.ERROR}cwebp.exe not found{CC.RESET}",
    )

    def check(self):
        return self.value.check()

    @classmethod
    def formats(cls) -> list[str]:
        return [support.name.lower() for support in cls]

    @classmethod
    def check_format(cls, format: str) -> bool:
        try:
            return cls[format.upper()].check()
        except KeyError:
            return False