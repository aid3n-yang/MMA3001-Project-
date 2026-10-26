
from pathlib import Path

from src.data_cleaning import load_clean_temperature_data
from src.experiment import (
    run_reconstruction_experiment,
    summarise_accuracy,
    summarise_robustness,
)


# Project settings
DATA_PATH = Path("data/raw/5EnvSensor_MayToDec2024_180kRows.csv")
SENSOR_ID = 6012002000869

GAP_SIZES = [1, 2, 3, 6, 9, 12]
CONTEXT_POINTS = 4
TRIALS_PER_GAP = 100
RANDOM_SEED = 42


def main():
    """
    Run the complete temperature reconstruction experiment.

    The workflow:
    1. Loads and cleans the selected temperature sensor.
    2. Runs the withheld-data reconstruction experiment.
    3. Generates accuracy and robustness summaries.
    4. Saves the results as CSV files.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {DATA_PATH}. "
            "Place the environmental CSV inside data/raw/ "
            "before running the project."
        )

    print("Loading and cleaning temperature data...")

    data = load_clean_temperature_data(
        DATA_PATH,
        sensor_id=SENSOR_ID
    )

    print(f"Clean measurements: {len(data)}")

    print("Running reconstruction experiment...")

    results = run_reconstruction_experiment(
        data,
        gap_sizes=GAP_SIZES,
        context_points=CONTEXT_POINTS,
        trials_per_gap=TRIALS_PER_GAP,
        seed=RANDOM_SEED
    )

    accuracy = summarise_accuracy(results)
    robustness = summarise_robustness(results)

    # Convert the number of missing measurements into an approximate
    # duration using the sensor's roughly 10-minute sampling interval.
    accuracy["Approx_Duration_Min"] = accuracy["Gap Size"] * 10

    output_directory = Path("results/tables")
    output_directory.mkdir(parents=True, exist_ok=True)

    results.to_csv(
        output_directory / "all_experiment_trials.csv",
        index=False
    )

    accuracy.to_csv(
        output_directory / "accuracy_summary.csv",
        index=False
    )

    robustness.to_csv(
        output_directory / "robustness_summary.csv",
        index=False
    )

    print(f"Experiment complete: {len(results)} evaluations")
    print(f"Results saved to {output_directory}")

    print("\nAccuracy summary:")
    print(accuracy.to_string(index=False))


if __name__ == "__main__":
    main()
