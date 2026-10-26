
import json
import pandas as pd

from src.data_cleaning import extract_temperature


def test_extract_temperature_valid_record():
    """Check that temperature and timestamp are extracted correctly."""

    sample = [
        {
            "variable": {"name": "Temperature"},
            "values": [
                {
                    "time": 1700000000,
                    "value": 23.5
                }
            ]
        }
    ]

    json_text = json.dumps(sample)

    timestamp, temperature = extract_temperature(json_text)

    assert timestamp == 1700000000
    assert temperature == 23.5


def test_extract_temperature_missing_temperature():
    """Return None values when no temperature variable exists."""

    sample = [
        {
            "variable": {"name": "Humidity"},
            "values": [
                {
                    "time": 1700000000,
                    "value": 60
                }
            ]
        }
    ]

    json_text = json.dumps(sample)

    timestamp, temperature = extract_temperature(json_text)

    assert timestamp is None
    assert temperature is None


def test_extract_temperature_empty_values():
    """Return None values when the temperature measurement has no values."""

    sample = [
        {
            "variable": {"name": "Temperature"},
            "values": []
        }
    ]

    json_text = json.dumps(sample)

    timestamp, temperature = extract_temperature(json_text)

    assert timestamp is None
    assert temperature is None


def test_extract_temperature_invalid_json():
    """Invalid JSON should be handled without crashing."""

    timestamp, temperature = extract_temperature(
        "this is not valid json"
    )

    assert timestamp is None
    assert temperature is None
