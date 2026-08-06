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


ALERT_MESSAGE = "⚠️ Settimana non aggiornata — controlla settimana-corrente.md"
REST_MESSAGE = (
    "🔄 Oggi riposo. Ricordati di: loggare i risultati della settimana in "
    "log-settimanale.md e preparare (insieme a Claude) il dettaglio della settimana prossima."
)


def get_message_for_date(week: dict[str, tuple[str, str]], date_str: str) -> str:
    """Determina il testo da inviare per la data indicata."""
    if date_str not in week:
        return ALERT_MESSAGE
    giorno, sessione = week[date_str]
    if sessione.strip().upper() == "RIPOSO":
        return REST_MESSAGE
    return f"🏋️ Allenamento di oggi ({giorno} {date_str}):\n{sessione}"


def should_run(now) -> bool:
    """True solo se l'ora locale di Roma è le 9 — guardia contro il doppio trigger cron UTC."""
    return now.hour == 9
