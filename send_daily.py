"""Bot Telegram: invia la sessione Hyrox del giorno o il promemoria di riposo."""

import re

ROW_PATTERN = re.compile(
    r"^\|\s*(?P<giorno>[^|]+?)\s*\|\s*(?P<data>\d{4}-\d{2}-\d{2})\s*\|\s*(?P<sessione>.+?)\s*\|\s*$",
    re.MULTILINE,
)


def parse_week_table(markdown_text: str) -> dict[str, tuple[str, str]]:
    """Estrae le righe della tabella settimanale in un dict data -> (giorno, sessione)."""
    week: dict[str, tuple[str, str]] = {}
    for match in ROW_PATTERN.finditer(markdown_text):
        week[match.group("data")] = (match.group("giorno"), match.group("sessione"))
    return week
