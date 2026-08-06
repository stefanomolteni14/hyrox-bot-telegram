"""Bot Telegram: invia la sessione Hyrox del giorno o il promemoria di riposo."""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ROME_TZ = ZoneInfo("Europe/Rome")
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
WEEK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settimana-corrente.md")

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


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Invia `text` alla chat Telegram indicata, tramite l'API sendMessage."""
    url = TELEGRAM_API_URL.format(token=token)
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request) as response:
        response.read()


def main(now: "datetime | None" = None) -> None:
    now = now or datetime.now(ROME_TZ)
    if not should_run(now):
        return

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    with open(WEEK_FILE, encoding="utf-8") as f:
        week = parse_week_table(f.read())

    date_str = now.strftime("%Y-%m-%d")
    message = get_message_for_date(week, date_str)
    send_telegram_message(token, chat_id, message)


if __name__ == "__main__":
    main()
