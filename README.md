# MMA3001 Project – Reconstruction of Missing Indoor Temperature Data

## Project Overview

Indoor environmental monitoring relies on continuous and reliable sensor data, particularly when analysing building performance and HVAC behaviour. However, real sensor systems are not always perfect, and measurements can be lost due to sensor faults, communication issues, or temporary outages, leaving gaps within otherwise useful datasets.

This project investigates how effectively numerical methods can reconstruct these missing indoor temperature measurements using data from the Monash Smart Infrastructure (MSI) environmental dataset.

The main focus is not simply on finding the method with the lowest error, but on understanding how each method behaves as the amount of missing data increases. This allows the methods to be compared not only in terms of accuracy, but also reliability, computational cost, and overall suitability for an engineering application.

## The Choice of Numerical Methods

Four reconstruction methods are compared:

- Local mean imputation
- Linear interpolation
- Cubic spline interpolation
- Piecewise Cubic Hermite Interpolating Polynomial (PCHIP)

Local mean imputation provides a simple baseline for comparison. It replaces the missing measurements using the average of the known measurements surrounding the gap, without attempting to represent the changing behaviour of the temperature signal.

Linear interpolation provides a simple numerical alternative by assuming a straight-line change between known measurements.

Cubic spline interpolation introduces a smoother reconstruction by fitting cubic functions between surrounding data points. Although this allows more complex behaviour to be represented, the additional curvature may not always reflect the actual temperature trend.

PCHIP was included as another cubic interpolation method, but with the advantage of preserving the local shape of the data and reducing unnecessary overshoot.

The purpose of comparing these methods is not to test as many algorithms as possible. Instead, the comparison focuses on a small set of methods with clearly different levels of complexity and behaviour.

## Which Dataset?

The original environmental sensor dataset contains approximately 180,000 database records, with individual measurements stored inside JSON fields.

Temperature measurements were extracted and cleaned from sensor:

`6012002000869`

This sensor was selected after examining the available sensors and their timestamp behaviour. Several sensors contained large numbers of repeated timestamps or irregular sampling patterns, which would make interpolation difficult to evaluate fairly.

Sensor `6012002000869` provided a much more consistent sampling interval of approximately 10 minutes and produced 13,800 unique temperature measurements after duplicate timestamps were removed.

The raw environmental dataset is not included in this repository due to its large file size.

To reproduce the cleaning process, the CSV file should be placed inside:

```text
data/raw/
```

## Experimental Method

The reconstruction methods are validated by artificially removing measurements from parts of the dataset where the real temperature values are already known.

This allows the hidden measurements to be kept as ground truth while each numerical method attempts to reconstruct them.

Only continuous sections of the dataset are used for testing. A section is treated as continuous when consecutive measurements are separated by approximately 9–11 minutes.

Six different missing-data gap sizes are evaluated:

- 1 consecutive measurement (~10 min)
- 2 consecutive measurements (~20 min)
- 3 consecutive measurements (~30 min)
- 6 consecutive measurements (~60 min)
- 9 consecutive measurements (~90 min)
- 12 consecutive measurements (~120 min)

For every gap size, 100 valid windows are sampled using a fixed random seed of `42`. This allows the experiment to be reproduced using the same selected windows.

Each test window contains four known temperature measurements before the missing region and four known measurements after it.

The reconstructed values are compared against the original measurements using:

- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)

MAE provides an indication of the average reconstruction error, while RMSE gives greater weight to larger individual errors.

Average performance alone may also hide occasional poor reconstructions. For this reason, robustness is further examined using median MAE, standard deviation, maximum MAE, and 95th-percentile MAE.

Computational runtime is also measured to determine whether improved reconstruction accuracy comes with a meaningful increase in computational cost.

## Main Findings

A clear pattern appears as the amount of missing data increases.

Linear interpolation performs particularly well for short gaps. For one missing measurement, it achieved the lowest average MAE while also having the lowest computational cost of all tested methods.

PCHIP becomes more effective as the missing interval becomes larger. For gaps of approximately 60, 90, and 120 minutes, PCHIP produced lower average MAE and RMSE than linear interpolation.

At the longest tested gap of 12 consecutive measurements, the average MAE values were approximately:

- Local Mean: 0.372 °C
- Cubic Spline: 0.268 °C
- Linear: 0.235 °C
- PCHIP: 0.222 °C

The results suggest that greater numerical complexity does not automatically produce better reconstruction.

Cubic spline interpolation creates a smoother curve than linear interpolation, but this additional curvature did not consistently improve accuracy. In some cases, the spline introduced behaviour that was not strongly supported by the surrounding measurements.

Local mean imputation performed worst overall. This became especially noticeable for longer gaps, where replacing an entire missing region with one constant value was unable to represent the changing temperature trend.

All methods also became less accurate and less consistent as the number of missing measurements increased.

One of the most important observations came from examining a difficult long-gap reconstruction. The real temperature increased sharply and reached a peak entirely within the hidden interval. None of the methods could fully reconstruct this behaviour because the surrounding known measurements did not contain enough information about the hidden peak.

This highlights an important limitation of interpolation. Even a mathematically sophisticated method cannot recover behaviour that is not represented in the available data.

## Computational Performance

Runtime testing showed a large relative difference between the simpler and more complex methods.

Linear interpolation required approximately 0.002–0.004 ms per reconstruction, making it the fastest method tested.

Local mean imputation required approximately 0.010–0.014 ms, while cubic spline and PCHIP generally required around 0.23–0.37 ms.

Although PCHIP and cubic spline are considerably slower than linear interpolation in relative terms, their absolute runtimes remain extremely small for this application.

This creates an important engineering trade-off. Linear interpolation offers excellent speed and strong short-gap accuracy, while PCHIP provides improved reconstruction for longer gaps at a computational cost that is still negligible for a dataset of this size.

## Repository Structure

```text
MMA3001-Project-/
│
├── src/
│   ├── __init__.py
│   ├── data_cleaning.py
│   ├── reconstruction.py
│   └── experiment.py
│
├── tests/
│   ├── test_data_cleaning.py
│   └── test_reconstruction.py
│
├── results/
│   ├── figures/
│   └── tables/
│
├── reports/
│   └── test_report.txt
│
├── docs/
├── data/
│   └── raw/
│
├── pytest.ini
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

The exact package versions used during development are recorded in `requirements.txt`.

## Running the Tests

The automated test suite can be run using:

```bash
pytest -v
```

The tests check several parts of the project, including:

- extraction of valid temperature measurements from JSON data
- handling of missing, empty, and malformed sensor records
- correct MAE and RMSE calculations
- reconstruction of constant temperature signals
- reconstruction of known linear temperature trends
- correct reconstruction output dimensions

A saved pytest report is available at:

```text
reports/test_report.txt
```

All eight automated tests passed during the final verification of the project.

## Reproducing the Experiment

The original environmental CSV dataset should first be placed inside:

```text
data/raw/
```

The selected sensor can then be loaded and cleaned using:

```python
from src.data_cleaning import load_clean_temperature_data

data = load_clean_temperature_data(
    "data/raw/5EnvSensor_MayToDec2024_180kRows.csv",
    sensor_id=6012002000869
)
```

The reconstruction experiment can then be reproduced using:

```python
from src.experiment import run_reconstruction_experiment

results = run_reconstruction_experiment(
    data,
    gap_sizes=[1, 2, 3, 6, 9, 12],
    context_points=4,
    trials_per_gap=100,
    seed=42
)
```

This produces:

```text
6 gap sizes × 100 trials × 4 methods = 2,400 evaluations
```

The fixed random seed ensures that the same experimental windows are selected when the experiment is repeated.

## Results

Generated result tables are stored in:

```text
results/tables/
```

These include:

- all individual experimental trials
- reconstruction accuracy summaries
- robustness summaries
- runtime summaries

Generated figures are stored in:

```text
results/figures/
```

These include the MAE and RMSE sensitivity plots, as well as a reconstruction example from a challenging long missing-data interval.

## Documentation

HTML documentation generated using `pdoc` is stored inside:

```text
docs/
```

The documentation covers the data-cleaning, reconstruction, and experimental modules used throughout the project.

## Limitations

The results are based on one selected indoor temperature sensor. While this allowed the numerical methods to be compared under consistent conditions, the exact performance may not carry across to different sensors, buildings, environmental variables, or sampling frequencies.

The experiment also creates artificial gaps within otherwise continuous data. This provides known ground truth and allows the methods to be compared fairly, but real sensor failures may occur under different conditions.

Another limitation is the availability of surrounding information. As the missing interval becomes larger, there is less evidence available about what occurred inside the gap. Short-term changes or temperature peaks may therefore be underestimated or missed entirely.

For this reason, reconstructed values should not automatically be treated as equivalent to real sensor measurements. The reliability of the reconstruction depends strongly on both the gap duration and the behaviour of the temperature signal surrounding it.
