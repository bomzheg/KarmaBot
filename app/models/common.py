from enum import Enum


class TypeRestriction(Enum):
    no_one = "no_one"
    ro = "ro"
    ban = "ban"
    warn = "warn"
    karmic_ro = "karmic_ro"
    karmic_ban = "karmic_ban"

    def get_emoji(self):
        return {
            self.warn: "❗",
            self.ro: "‼",
            self.ban: "🚫",
            self.karmic_ro: "🌀",
            self.karmic_ban: "🌀🚫",
        }[self]
