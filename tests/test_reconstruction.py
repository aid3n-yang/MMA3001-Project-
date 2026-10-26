
import numpy as np
import pandas as pd

from src.reconstruction import (
    reconstruct_window,
    calculate_metrics
)


def test_calculate_metrics():
    """Check that MAE and RMSE are calculated correctly."""

    actual = np.array([1.0, 2.0, 3.0])
    predicted = np.array([1.0, 2.0, 4.0])

    mae, rmse = calculate_metrics(actual, predicted)

    assert np.isclose(mae, 1 / 3)
    assert np.isclose(rmse, np.sqrt(1 / 3))


def test_constant_temperature_reconstruction():
    """
    All reconstruction methods should exactly reproduce
    a constant temperature signal.
    """

    window = pd.DataFrame({
        "datetime": pd.date_range(
            start="2024-01-01",
            periods=11,
            freq="10min",
            tz="UTC"
        ),
        "temperature": np.full(11, 22.0)
    })

    output = reconstruct_window(
        window,
        gap_size=3,
        context_points=4
    )

    for method in [
        "Mean",
        "Linear",
        "Cubic Spline",
        "PCHIP"
    ]:
        assert np.allclose(
            output[method],
            22.0
        )


def test_linear_temperature_reconstruction():
    """
    Interpolation methods should reconstruct an exactly
    linear temperature trend.
    """

    temperatures = np.linspace(
        20.0,
        25.0,
        11
    )

    window = pd.DataFrame({
        "datetime": pd.date_range(
            start="2024-01-01",
            periods=11,
            freq="10min",
            tz="UTC"
        ),
        "temperature": temperatures
    })

    output = reconstruct_window(
        window,
        gap_size=3,
        context_points=4
    )

    actual = output["actual"]

    for method in [
        "Linear",
        "Cubic Spline",
        "PCHIP"
    ]:
        assert np.allclose(
            output[method],
            actual
        )


def test_output_lengths():
    """Check that each reconstruction returns the expected number of values."""

    window = pd.DataFrame({
        "datetime": pd.date_range(
            start="2024-01-01",
            periods=14,
            freq="10min",
            tz="UTC"
        ),
        "temperature": np.linspace(
            21.0,
            23.0,
            14
        )
    })

    output = reconstruct_window(
        window,
        gap_size=6,
        context_points=4
    )

    assert len(output["actual"]) == 6

    for method in [
        "Mean",
        "Linear",
        "Cubic Spline",
        "PCHIP"
    ]:
        assert len(output[method]) == 6
