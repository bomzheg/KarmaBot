from enum import Enum


class TypeRestriction(Enum):
    ro = "ro"
    ban = "ban"
    warn = "warn"
    karmic_ro = "karmic_ro"
    karmic_ban = "karmic_ban"
