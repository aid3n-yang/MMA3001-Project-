
import json
import pandas as pd


def extract_temperature(json_text):
    """
    Extract a temperature measurement and timestamp from one sensor JSON record.

    Parameters
    ----------
    json_text : str
        JSON string containing environmental sensor measurements.

    Returns
    -------
    tuple
        A tuple containing (timestamp, temperature).
        Returns (None, None) if no valid temperature measurement is found.
    """

    try:
        measurements = json.loads(json_text)

        for measurement in measurements:
            if measurement["variable"]["name"] == "Temperature":

                values = measurement.get("values", [])

                if len(values) == 0:
                    return None, None

                timestamp = values[0].get("time")
                temperature = values[0].get("value")

                return timestamp, temperature

    except (TypeError, json.JSONDecodeError, KeyError):
        return None, None

    return None, None


def load_clean_temperature_data(csv_path, sensor_id):
    """
    Load and clean temperature measurements for one environmental sensor.

    Parameters
    ----------
    csv_path : str
        Path to the raw environmental sensor CSV file.
    sensor_id : int
        Sensor identifier to extract.

    Returns
    -------
    pandas.DataFrame
        Chronologically ordered temperature measurements with duplicate
        timestamps removed.
    """

    raw_data = pd.read_csv(
        csv_path,
        usecols=["sensorid", "jsondata"]
    )

    extracted = raw_data["jsondata"].apply(extract_temperature)

    temperature_data = pd.DataFrame(
        extracted.tolist(),
        columns=["timestamp", "temperature"]
    )

    temperature_data["sensorid"] = raw_data["sensorid"].values

    # Keep only the selected sensor.
    sensor_data = temperature_data[
        temperature_data["sensorid"] == sensor_id
    ].copy()

    # Remove records where temperature extraction failed.
    sensor_data = sensor_data.dropna(
        subset=["timestamp", "temperature"]
    )

    # Convert Unix timestamps into UTC datetimes.
    sensor_data["datetime"] = pd.to_datetime(
        sensor_data["timestamp"],
        unit="s",
        utc=True
    )

    # Duplicate timestamps in the selected dataset contain the same
    # temperature measurement, so only one observation is retained.
    sensor_data = (
        sensor_data
        .drop_duplicates(subset="datetime")
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    # Calculate the time between consecutive observations.
    sensor_data["time_gap_minutes"] = (
        sensor_data["datetime"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    return sensor_data
