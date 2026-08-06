import json
from datetime import datetime
from unittest.mock import patch, MagicMock

import send_daily
from send_daily import parse_week_table
from send_daily import get_message_for_date, should_run, ALERT_MESSAGE, REST_MESSAGE
from send_daily import send_telegram_message

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


def test_send_telegram_message_calls_correct_endpoint():
    with patch("send_daily.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = MagicMock()
        send_telegram_message("FAKE_TOKEN", "12345", "ciao")

        assert mock_urlopen.called
        request = mock_urlopen.call_args[0][0]
        assert request.full_url == "https://api.telegram.org/botFAKE_TOKEN/sendMessage"
        body = json.loads(request.data.decode("utf-8"))
        assert body == {"chat_id": "12345", "text": "ciao"}


def test_main_sends_message_when_should_run_true(tmp_path, monkeypatch):
    week_file = tmp_path / "settimana-corrente.md"
    week_file.write_text(
        "| Giorno | Data | Sessione |\n|---|---|---|\n"
        "| Lunedì | 2026-08-10 | Corsa soglia |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(send_daily, "WEEK_FILE", str(week_file))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "FAKE_TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")

    with patch("send_daily.send_telegram_message") as mock_send:
        send_daily.main(now=datetime(2026, 8, 10, 9, 0))

        mock_send.assert_called_once_with("FAKE_TOKEN", "12345", send_daily.get_message_for_date(
            {"2026-08-10": ("Lunedì", "Corsa soglia")}, "2026-08-10"
        ))


def test_main_does_nothing_when_should_run_false(tmp_path, monkeypatch):
    week_file = tmp_path / "settimana-corrente.md"
    week_file.write_text(
        "| Giorno | Data | Sessione |\n|---|---|---|\n"
        "| Lunedì | 2026-08-10 | Corsa soglia |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(send_daily, "WEEK_FILE", str(week_file))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "FAKE_TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")

    with patch("send_daily.send_telegram_message") as mock_send:
        send_daily.main(now=datetime(2026, 8, 10, 14, 0))

        mock_send.assert_not_called()
