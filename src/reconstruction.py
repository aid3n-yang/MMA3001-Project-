
import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator


def calculate_metrics(actual, predicted):
    """
    Calculate MAE and RMSE between actual and predicted values.

    Parameters
    ----------
    actual : array-like
        Ground-truth temperature values.
    predicted : array-like
        Reconstructed temperature values.

    Returns
    -------
    tuple
        Mean absolute error and root mean square error.
    """

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    return mae, rmse


def reconstruct_window(window, gap_size, context_points=4):
    """
    Reconstruct artificially hidden temperature measurements using
    multiple numerical methods.

    Parameters
    ----------
    window : pandas.DataFrame
        Continuous temperature observations containing 'datetime'
        and 'temperature' columns.
    gap_size : int
        Number of consecutive measurements to hide.
    context_points : int, optional
        Number of known observations retained on each side of the gap.

    Returns
    -------
    dict
        Ground truth and reconstructed values for Mean, Linear,
        Cubic Spline, and PCHIP methods.
    """

    window = window.copy()

    time_minutes = (
        window["datetime"] - window["datetime"].iloc[0]
    ).dt.total_seconds().to_numpy() / 60

    hidden_start = context_points
    hidden_end = context_points + gap_size

    hidden_positions = np.arange(
        hidden_start,
        hidden_end
    )

    actual = window["temperature"].iloc[
        hidden_start:hidden_end
    ].to_numpy()

    masked_temperature = window["temperature"].copy()

    masked_temperature.iloc[
        hidden_start:hidden_end
    ] = np.nan

    known_mask = masked_temperature.notna().to_numpy()

    x_known = time_minutes[known_mask]
    y_known = masked_temperature[known_mask].to_numpy()

    x_missing = time_minutes[hidden_positions]

    mean_predictions = np.full(
        gap_size,
        np.mean(y_known)
    )

    linear_predictions = np.interp(
        x_missing,
        x_known,
        y_known
    )

    cubic_model = CubicSpline(
        x_known,
        y_known
    )

    cubic_predictions = cubic_model(
        x_missing
    )

    pchip_model = PchipInterpolator(
        x_known,
        y_known
    )

    pchip_predictions = pchip_model(
        x_missing
    )

    return {
        "actual": actual,
        "Mean": mean_predictions,
        "Linear": linear_predictions,
        "Cubic Spline": cubic_predictions,
        "PCHIP": pchip_predictions
    }
