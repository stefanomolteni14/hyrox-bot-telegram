from send_daily import parse_week_table

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
