
import numpy as np
import pandas as pd

from .reconstruction import reconstruct_window, calculate_metrics


def find_valid_window_starts(
    data,
    gap_size,
    context_points=4,
    min_interval=9,
    max_interval=11
):
    """
    Find starting indices for continuous temperature-data windows.

    A window is considered continuous when every consecutive timestamp
    is separated by between min_interval and max_interval minutes.

    Parameters
    ----------
    data : pandas.DataFrame
        Temperature dataset containing a 'datetime' column.
    gap_size : int
        Number of consecutive measurements that will be hidden.
    context_points : int, optional
        Number of retained observations on each side of the hidden gap.
    min_interval : float, optional
        Minimum acceptable sampling interval in minutes.
    max_interval : float, optional
        Maximum acceptable sampling interval in minutes.

    Returns
    -------
    list
        Starting row indices of valid continuous windows.
    """

    window_length = 2 * context_points + gap_size
    valid_starts = []

    for start in range(len(data) - window_length + 1):

        window = data.iloc[
            start:start + window_length
        ]

        intervals = (
            window["datetime"]
            .diff()
            .dt.total_seconds()
            .div(60)
            .iloc[1:]
        )

        if intervals.between(
            min_interval,
            max_interval
        ).all():
            valid_starts.append(start)

    return valid_starts


def evaluate_window(
    window,
    gap_size,
    context_points=4
):
    """
    Evaluate all reconstruction methods on one withheld-data window.

    Returns
    -------
    list of dict
        MAE and RMSE for each reconstruction method.
    """

    reconstructed = reconstruct_window(
        window,
        gap_size=gap_size,
        context_points=context_points
    )

    actual = reconstructed["actual"]

    results = []

    for method in [
        "Mean",
        "Linear",
        "Cubic Spline",
        "PCHIP"
    ]:

        mae, rmse = calculate_metrics(
            actual,
            reconstructed[method]
        )

        results.append({
            "Method": method,
            "MAE": mae,
            "RMSE": rmse
        })

    return results


def run_reconstruction_experiment(
    data,
    gap_sizes=(1, 2, 3, 6, 9, 12),
    context_points=4,
    trials_per_gap=100,
    seed=42
):
    """
    Run repeated withheld-data reconstruction experiments.

    For each gap size, continuous data windows are identified and a
    reproducible random sample is selected. Known temperature values
    are then hidden and reconstructed using each numerical method.

    Parameters
    ----------
    data : pandas.DataFrame
        Cleaned temperature dataset.
    gap_sizes : sequence of int, optional
        Numbers of consecutive measurements to hide.
    context_points : int, optional
        Number of known observations retained on each side of the gap.
    trials_per_gap : int, optional
        Number of test windows sampled for each gap size.
    seed : int, optional
        Random seed used to make sampling reproducible.

    Returns
    -------
    pandas.DataFrame
        Trial-level MAE and RMSE results.
    """

    rng = np.random.default_rng(seed)
    all_results = []

    for gap_size in gap_sizes:

        valid_starts = find_valid_window_starts(
            data,
            gap_size=gap_size,
            context_points=context_points
        )

        if len(valid_starts) < trials_per_gap:
            raise ValueError(
                f"Only {len(valid_starts)} valid windows exist "
                f"for gap size {gap_size}, but "
                f"{trials_per_gap} trials were requested."
            )

        selected_starts = rng.choice(
            valid_starts,
            size=trials_per_gap,
            replace=False
        )

        window_length = (
            2 * context_points
            + gap_size
        )

        for trial_number, start in enumerate(
            selected_starts,
            start=1
        ):

            window = data.iloc[
                start:start + window_length
            ].copy()

            window_results = evaluate_window(
                window,
                gap_size=gap_size,
                context_points=context_points
            )

            for result in window_results:

                result["Gap Size"] = gap_size
                result["Trial"] = trial_number
                result["Start Index"] = int(start)

                all_results.append(result)

    return pd.DataFrame(all_results)


def summarise_accuracy(results):
    """
    Summarise reconstruction accuracy by gap size and method.
    """

    return (
        results
        .groupby(["Gap Size", "Method"])
        .agg(
            Mean_MAE=("MAE", "mean"),
            Std_MAE=("MAE", "std"),
            Mean_RMSE=("RMSE", "mean"),
            Std_RMSE=("RMSE", "std")
        )
        .reset_index()
    )


def summarise_robustness(results):
    """
    Summarise variability and worst-case reconstruction performance.
    """

    return (
        results
        .groupby(["Gap Size", "Method"])
        .agg(
            Mean_MAE=("MAE", "mean"),
            Median_MAE=("MAE", "median"),
            Std_MAE=("MAE", "std"),
            Max_MAE=("MAE", "max"),
            P95_MAE=("MAE", lambda x: x.quantile(0.95))
        )
        .reset_index()
    )
