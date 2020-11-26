from enum import Enum


class TypeRestriction(Enum):
    ro = "ro"
    ban = "ban"
    warn = "warn"
    auto_for_negative_carma = "auto_for_negative_carma"
