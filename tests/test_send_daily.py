from datetime import datetime

from send_daily import parse_week_table
from send_daily import get_message_for_date, should_run, ALERT_MESSAGE, REST_MESSAGE

WEEK_TABLE = """\
# Settimana corrente

| Giorno | Data | Sessione |
|---|---|---|
| Lunedì | 2026-08-10 | Corsa soglia: 6x1km ritmo soglia, rec 90 sec |
| Martedì | 2026-08-11 | Forza inferiore pesante + 10 min corsa compromessa |
| Domenica | 2026-08-16 | RIPOSO |
"""


def test_sanity():
    assert True


def test_parse_week_table_extracts_rows():
    week = parse_week_table(WEEK_TABLE)
    assert week["2026-08-10"] == ("Lunedì", "Corsa soglia: 6x1km ritmo soglia, rec 90 sec")


def test_parse_week_table_extracts_riposo():
    week = parse_week_table(WEEK_TABLE)
    assert week["2026-08-16"] == ("Domenica", "RIPOSO")


def test_parse_week_table_ignores_header_and_separator():
    week = parse_week_table(WEEK_TABLE)
    assert len(week) == 3
    assert "Giorno" not in week


SAMPLE_WEEK = {
    "2026-08-10": ("Lunedì", "Corsa soglia: 6x1km ritmo soglia, rec 90 sec"),
    "2026-08-16": ("Domenica", "RIPOSO"),
}


def test_get_message_for_date_returns_workout_text():
    msg = get_message_for_date(SAMPLE_WEEK, "2026-08-10")
    assert "Corsa soglia: 6x1km ritmo soglia, rec 90 sec" in msg
    assert "Lunedì" in msg


def test_get_message_for_date_returns_rest_message():
    msg = get_message_for_date(SAMPLE_WEEK, "2026-08-16")
    assert msg == REST_MESSAGE


def test_get_message_for_date_returns_alert_when_missing():
    msg = get_message_for_date(SAMPLE_WEEK, "2026-08-11")
    assert msg == ALERT_MESSAGE


def test_should_run_true_at_9():
    assert should_run(datetime(2026, 8, 10, 9, 2)) is True


def test_should_run_false_other_hours():
    assert should_run(datetime(2026, 8, 10, 7, 0)) is False
    assert should_run(datetime(2026, 8, 10, 10, 0)) is False
