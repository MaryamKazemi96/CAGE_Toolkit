# CAGE Toolkit

**Tools for processing, inspecting, and analyzing human and robot trajectories from the CAGE dataset.**

<p align="center">
  <img src="environment.jpg" alt="CAGE tracking environment" width="500">
</p>
<p align="center"> <em>Overview of the experimental environment used for CAGE data collection.</em> </p>

## Features

* Parse OptiTrack CSV recordings
* Normalize coordinate systems
* Detect human and robot tracks
* Trim trajectories to valid motion periods
* Check tracking quality
* Compute trajectory and motion metrics
* Compute THÖR-style trajectory statistics
* Analyze minimum distances between people
* Visualize trajectories and sensor data
* Analyze participant survey data
* Generate reproducible dataset-level summaries
* Configure dataset-specific parameters through YAML

## Installation

Clone the repository:

```bash
git clone https://github.com/MaryamKazemi96/tracking-toolkit.git
cd tracking-toolkit
```

## Dataset Organization

The toolkit expects the OptiTrack recordings to be organized by session.

A typical structure is:

```text
data/
└── OptiTrack/
    ├── raw/
    │   ├── session 1/
    │   ├── session 2/
    │   ├── ...
    │   └── session 8/
    │
    └── solved/
        ├── session 1/
        ├── session 2/
        ├── ...
        └── session 8/
```

Each session contains recordings for the corresponding scenarios.

## Configuration

Dataset-specific parameters are stored in:

```text
config/recordings.yaml
```

For example:

```yaml
dataset:
  fps: 120
  up_axis: y
  coordinate_system: global
```

The configuration file also defines:

* Available sessions and scenarios
* Participant rigid bodies
* Robot rigid bodies
* Preprocessing parameters

## Quick Start

### Inspect the Dataset

```bash
python scripts/inspect_dataset.py
```

This provides an overview of the available recordings and tracked rigid bodies.

### Check Tracking Quality

```bash
python scripts/check_quality.py
```

This can be used to identify potential tracking problems before further analysis.

### Compute Trajectory Metrics

```bash
python scripts/compute_thor_metrics.py
```

The toolkit computes:

* Tracking duration
* Motion speed
* Trajectory curvature
* Perception noise
* Minimum distance between people

### Visualize Trajectories

```bash
python scripts/plot_scenario_trajectories.py
```

Additional visualization scripts are available in the `scripts/` directory.

Loading a Recording in Python

The toolkit provides a DatasetLoader for accessing individual recordings.

from pathlib import Path

from src.io.loader import DatasetLoader

loader = DatasetLoader(
    root=Path("data/OptiTrack/solved"),
    config_path=Path("config/recordings.yaml"),
)

recording = loader.load(
    session=1,
    scenario=3,
)

print(recording["session"])
print(recording["scenario"])
print(recording["humans"])
print(recording["robots"])

The loader handles the dataset configuration and coordinate normalization before returning the recording data.

## Processing Pipeline

The typical processing workflow is:

OptiTrack recordings
        │
        ▼
     Parsing
        │
        ▼
Coordinate normalization
        │
        ▼
Human / robot detection
        │
        ▼
Trajectory trimming
        │
        ▼
Tracking quality checks
        │
        ▼
Trajectory metrics
        │
        ▼
Visualization & analysis

Each stage can also be used independently through the modules in src/.

## Visualization

The repository contains scripts for visualizing trajectories, metrics, sensor data, and experimental recordings.

Examples include:

python scripts/plot_scenario_trajectories.py
python scripts/plot_min_human_distance.py
python scripts/plot_thor_metrics.py

For ROS bag sensor visualization:

python scripts/plot_rosbag_sensors.py

## Survey Analysis

The toolkit also contains utilities for processing and analyzing participant survey data.

The main components are:

src/survey/
├── data.py
├── plots.py
└── stats.py

Survey analysis can be run using:

python scripts/analyze_survey.py

## Paper

For details about the dataset, experimental setup, and analysis, please see the  paper:
CAGE: A High-Precision Multimodal Human-Robot Coexistence Dataset with Explicit Robot Intent Communication

Paper

## Dataset

The complete dataset and additional information are available on the dataset webpage:

Dataset Webpage
## License



## Acknowledgements

This work was developed as part of research on human–robot coexistence and multi-robot systems at Aalto University.
## Contact
The cage toolkit has been developed by Maryam Kazemi. For questions, issues, or further information, please contact: maryam.kazemieskeri@aalto.fi.
