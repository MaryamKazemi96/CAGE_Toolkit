
# """
# Paper-quality minimum human-robot distance plot.

# Computes the minimum Euclidean distance between the robot and any
# tracked human using OptiTrack trajectories only.

# Output:
#     results/paper_figures/min_human_robot_distance_s5_s4.png
#     results/paper_figures/min_human_robot_distance_s5_s4.pdf
# """

# from __future__ import annotations

# from pathlib import Path

# import matplotlib.pyplot as plt
# import numpy as np

# from src.io.loader import DatasetLoader
# from src.preprocessing.presence import detect_presence
# from src.preprocessing.trim import trim


# # ---------------------------------------------------------------------
# # Configuration
# # ---------------------------------------------------------------------

# ROOT_SOLVED = "data/OptiTrack/solved"
# ROOT_RAW = "data/OptiTrack/raw"
# CONFIG = "config/recordings.yaml"

# SESSION = 1
# SCENARIO = 4

# OUTPUT = Path("results/paper_figures")
# OUTPUT.mkdir(parents=True, exist_ok=True)


# # ---------------------------------------------------------------------
# # Distance computation
# # ---------------------------------------------------------------------

# def compute_min_human_robot_distance(
#     df,
#     robot,
#     humans,
#     frame_rate,
# ):
#     """
#     Compute the minimum 2-D distance between the robot and any human
#     at every OptiTrack frame.
#     """

#     robot_x = f"{robot}.position.x"
#     robot_y = f"{robot}.position.y"

#     robot_xy = df[[robot_x, robot_y]].to_numpy(dtype=float)

#     human_positions = []

#     for human in humans:

#         x_col = f"{human}.position.x"
#         y_col = f"{human}.position.y"

#         if x_col not in df.columns or y_col not in df.columns:
#             continue

#         xy = df[[x_col, y_col]].to_numpy(dtype=float)
#         human_positions.append(xy)

#     if not human_positions:
#         raise ValueError("No valid human trajectories found.")

#     # Shape:
#     # humans x frames x 2
#     human_xy = np.stack(human_positions, axis=0)

#     # Shape:
#     # humans x frames
#     distances = np.linalg.norm(
#         human_xy - robot_xy[None, :, :],
#         axis=2,
#     )

#     # Ignore missing trajectories.
#     distances[~np.isfinite(distances)] = np.inf

#     min_distance = np.min(distances, axis=0)

#     time = np.arange(len(min_distance)) / frame_rate

#     return time, min_distance


# # ---------------------------------------------------------------------
# # Main
# # ---------------------------------------------------------------------

# def main():

#     solved_loader = DatasetLoader(
#         root=ROOT_SOLVED,
#         config=CONFIG,
#     )

#     raw_loader = DatasetLoader(
#         root=ROOT_RAW,
#         config=CONFIG,
#     )

#     # -------------------------------------------------------------
#     # Load data
#     # -------------------------------------------------------------

#     _, raw_df, info = raw_loader.load(
#         session=SESSION,
#         scenario=SCENARIO,
#     )

#     _, solved_df, _ = solved_loader.load(
#         session=SESSION,
#         scenario=SCENARIO,
#     )

#     # -------------------------------------------------------------
#     # Trim using the same presence logic used elsewhere
#     # -------------------------------------------------------------

#     waiting_area_x = raw_loader.config[
#         "preprocessing"
#     ]["waiting_area_x"]

#     presence = detect_presence(
#         df=raw_df,
#         bodies=info["humans"] + info["robots"],
#         waiting_area_x=waiting_area_x,
#     )

#     solved_df = trim(
#         solved_df,
#         presence,
#     )

#     # -------------------------------------------------------------
#     # Robot
#     # -------------------------------------------------------------

#     robots = info["robots"]

#     if not robots:
#         raise ValueError(
#             f"No robot specified for session {SESSION}, "
#             f"scenario {SCENARIO}."
#         )

#     if len(robots) > 1:
#         print(
#             f"[WARNING] Found {len(robots)} robots. "
#             f"Using the first one: {robots[0]}"
#         )

#     robot = robots[0]

#     # -------------------------------------------------------------
#     # Frame rate
#     # -------------------------------------------------------------

    

#     frame_rate = 120

#     if frame_rate is None:
#         raise ValueError(
#             "Could not determine OptiTrack frame rate."
#         )

#     print(f"Frame rate: {frame_rate:.2f} Hz")
#     print(f"Robot: {robot}")
#     print(f"Humans: {info['humans']}")

#     # -------------------------------------------------------------
#     # Compute distance
#     # -------------------------------------------------------------

#     time, distance = compute_min_human_robot_distance(
#         df=solved_df,
#         robot=robot,
#         humans=info["humans"],
#         frame_rate=frame_rate,
#     )

#     # Remove invalid values
#     valid = np.isfinite(distance)

#     time = time[valid]
#     distance = distance[valid]

#     # -------------------------------------------------------------
#     # Basic statistics
#     # -------------------------------------------------------------

#     print()
#     print("Minimum human-robot distance:")
#     print(f"  Mean   : {np.mean(distance):.3f} m")
#     print(f"  Median : {np.median(distance):.3f} m")
#     print(f"  Minimum: {np.min(distance):.3f} m")
#     print(f"  Maximum: {np.max(distance):.3f} m")

#     min_idx = np.argmin(distance)

#     # -------------------------------------------------------------
#     # Paper-quality figure
#     # -------------------------------------------------------------

#     fig, ax = plt.subplots(
#         figsize=(6.4, 3.6)
#     )

#     ax.plot(
#         time,
#         distance,
#         linewidth=1.4,
#         label="Minimum human–robot distance",
#     )

#     # Highlight the closest interaction
#     ax.scatter(
#         time[min_idx],
#         distance[min_idx],
#         s=32,
#         zorder=5,
#         label=(
#             f"Minimum = {distance[min_idx]:.2f} m"
#         ),
#     )

#     # Reference distance
#     ax.axhline(
#         1.0,
#         linestyle="--",
#         linewidth=1.0,
#         label="1 m reference",
#     )

#     # -------------------------------------------------------------
#     # Formatting
#     # -------------------------------------------------------------

#     ax.set_xlabel("Time (s)")
#     ax.set_ylabel("Minimum human–robot distance (m)")

#     ax.set_title(
#         f"Minimum human–robot distance "
#         f"(Session {SESSION}, Scenario {SCENARIO})"
#     )

#     ax.grid(
#         True,
#         linestyle=":",
#         linewidth=0.6,
#         alpha=0.6,
#     )

#     ax.set_xlim(
#         time[0],
#         time[-1],
#     )

#     # Keep the lower bound sensible
#     ax.set_ylim(
#         bottom=max(
#             0,
#             np.min(distance) - 0.15,
#         )
#     )

#     ax.legend(
#         frameon=False,
#         loc="upper right",
#         fontsize=8,
#     )

#     # Clean paper layout
#     ax.spines["top"].set_visible(False)
#     ax.spines["right"].set_visible(False)

#     fig.tight_layout()

#     # -------------------------------------------------------------
#     # Save
#     # -------------------------------------------------------------

#     png_path = (
#         OUTPUT
#         / f"min_human_robot_distance_s{SESSION}_s{SCENARIO}.png"
#     )

#     pdf_path = (
#         OUTPUT
#         / f"min_human_robot_distance_s{SESSION}_s{SCENARIO}.pdf"
#     )

#     fig.savefig(
#         png_path,
#         dpi=300,
#         bbox_inches="tight",
#     )

#     fig.savefig(
#         pdf_path,
#         bbox_inches="tight",
#     )

#     plt.close(fig)

#     print()
#     print(f"Saved:")
#     print(f"  {png_path}")
#     print(f"  {pdf_path}")


# if __name__ == "__main__":
#     main()


"""
Paper-quality human-robot distance figures.

For each scenario:
    - Compute minimum distance from Robot 1 to any human.
    - Compute minimum distance from Robot 2 to any human.
    - Generate one time-series plot for each robot.

Additionally:
    - Generate one box plot per robot comparing Scenarios 1-4.
    - Each dot represents one recording.
    - Each recording contributes one minimum-distance value.

All trajectories are obtained from OptiTrack only.

Outputs:
    results/paper_figures/
        min_human_robot_distance_robot1_s5_s1.png
        min_human_robot_distance_robot1_s5_s1.pdf
        ...
        min_human_robot_distance_robot2_s5_s4.png
        min_human_robot_distance_robot2_s5_s4.pdf

        min_human_robot_distance_robot1_by_scenario.png
        min_human_robot_distance_robot1_by_scenario.pdf

        min_human_robot_distance_robot2_by_scenario.png
        min_human_robot_distance_robot2_by_scenario.pdf
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.io.loader import DatasetLoader
from src.preprocessing.presence import detect_presence
from src.preprocessing.trim import trim


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

ROOT_SOLVED = "data/OptiTrack/solved"
ROOT_RAW = "data/OptiTrack/raw"
CONFIG = "config/recordings.yaml"

OUTPUT = Path("results/paper_figures")
OUTPUT.mkdir(parents=True, exist_ok=True)

FRAME_RATE = 120

SCENARIOS = [1, 2, 3, 4]

# Representative session for time-series figures.
REPRESENTATIVE_SESSION = 5


# ---------------------------------------------------------------------
# Distance computation
# ---------------------------------------------------------------------

def compute_min_human_robot_distance(
    df,
    robot,
    humans,
    frame_rate,
):
    """
    Compute the minimum 2-D distance between one robot and any human
    at every OptiTrack frame.
    """

    robot_x = f"{robot}.position.x"
    robot_y = f"{robot}.position.y"

    if robot_x not in df.columns or robot_y not in df.columns:
        raise ValueError(
            f"Robot trajectory not found for {robot}."
        )

    robot_xy = df[
        [robot_x, robot_y]
    ].to_numpy(dtype=float)

    human_positions = []

    for human in humans:

        x_col = f"{human}.position.x"
        y_col = f"{human}.position.y"

        if x_col not in df.columns or y_col not in df.columns:
            continue

        xy = df[
            [x_col, y_col]
        ].to_numpy(dtype=float)

        human_positions.append(xy)

    if not human_positions:
        raise ValueError(
            "No valid human trajectories found."
        )

    # humans × frames × 2
    human_xy = np.stack(
        human_positions,
        axis=0,
    )

    # humans × frames
    distances = np.linalg.norm(
        human_xy - robot_xy[None, :, :],
        axis=2,
    )

    # Ignore missing tracking data.
    distances[
        ~np.isfinite(distances)
    ] = np.inf

    # Minimum distance to any human at each frame.
    min_distance = np.min(
        distances,
        axis=0,
    )

    time = (
        np.arange(len(min_distance))
        / frame_rate
    )

    return time, min_distance


# ---------------------------------------------------------------------
# Load and preprocess one recording
# ---------------------------------------------------------------------

def load_recording(
    solved_loader,
    raw_loader,
    session,
    scenario,
):
    """
    Load and trim one recording.
    """

    _, raw_df, info = raw_loader.load(
        session=session,
        scenario=scenario,
    )

    _, solved_df, _ = solved_loader.load(
        session=session,
        scenario=scenario,
    )

    waiting_area_x = raw_loader.config[
        "preprocessing"
    ]["waiting_area_x"]

    presence = detect_presence(
        df=raw_df,
        bodies=info["humans"] + info["robots"],
        waiting_area_x=waiting_area_x,
    )

    solved_df = trim(
        solved_df,
        presence,
    )

    return solved_df, info


# ---------------------------------------------------------------------
# Time-series plot
# ---------------------------------------------------------------------

def plot_time_series(
    time,
    distance,
    session,
    scenario,
    robot_number,
):
    """
    Generate one paper-quality time-series plot.
    """

    min_idx = np.argmin(distance)

    minimum = distance[min_idx]

    fig, ax = plt.subplots(
        figsize=(6.4, 3.6)
    )

    ax.plot(
        time,
        distance,
        linewidth=1.3,
    )

    # Mark closest interaction.
    ax.scatter(
        time[min_idx],
        minimum,
        s=32,
        zorder=5,
        label=f"Minimum = {minimum:.2f} m",
    )

    # 1 m reference.
    ax.axhline(
        1.0,
        linestyle="--",
        linewidth=1.0,
        label="1 m reference",
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(
        "Minimum human–robot distance (m)"
    )

    # Useful during inspection.
    # Remove for final paper figure if desired.
    ax.set_title(
        f"Robot {robot_number} — "
        f"Scenario {scenario}"
    )

    ax.grid(
        True,
        linestyle=":",
        linewidth=0.6,
        alpha=0.6,
    )

    ax.set_xlim(
        time[0],
        time[-1],
    )

    # Avoid extreme outliers dominating the vertical axis.
    ymax = np.percentile(
        distance,
        99.5,
    )

    ax.set_ylim(
        0,
        max(1.1, ymax * 1.05),
    )

    ax.legend(
        frameon=False,
        loc="upper right",
        fontsize=8,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    filename = (
        f"min_human_robot_distance_"
        f"robot{robot_number}_"
        f"s{session}_s{scenario}"
    )

    png_path = OUTPUT / f"{filename}.png"
    pdf_path = OUTPUT / f"{filename}.pdf"

    fig.savefig(
        png_path,
        dpi=300,
        bbox_inches="tight",
    )

    fig.savefig(
        pdf_path,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


# ---------------------------------------------------------------------
# Collect recording-level minima
# ---------------------------------------------------------------------

def collect_recording_minima(
    solved_loader,
    raw_loader,
):
    """
    Compute one minimum-distance value per recording and robot.

    Returns:
        {
            1: {
                1: [...],
                2: [...],
                3: [...],
                4: [...],
            },
            2: {
                1: [...],
                2: [...],
                3: [...],
                4: [...],
            }
        }
    """

    results = {
        1: {
            scenario: []
            for scenario in SCENARIOS
        },
        2: {
            scenario: []
            for scenario in SCENARIOS
        },
    }

    for session_name, session_cfg in solved_loader.config[
        "sessions"
    ].items():

        session = int(
            session_name.split("_")[1]
        )

        for scenario in SCENARIOS:

            if scenario not in session_cfg["scenarios"]:
                continue

            try:

                solved_df, info = load_recording(
                    solved_loader,
                    raw_loader,
                    session,
                    scenario,
                )

                robots = info["robots"]

                if len(robots) < 2:
                    print(
                        f"[WARNING] Session {session}, "
                        f"Scenario {scenario}: "
                        f"only {len(robots)} robot(s) found."
                    )
                    continue

                for robot_index, robot in enumerate(
                    robots[:2],
                    start=1,
                ):

                    _, distance = (
                        compute_min_human_robot_distance(
                            df=solved_df,
                            robot=robot,
                            humans=info["humans"],
                            frame_rate=FRAME_RATE,
                        )
                    )

                    distance = distance[
                        np.isfinite(distance)
                    ]

                    if len(distance) == 0:
                        continue

                    recording_minimum = np.mean(
                        distance
                    )

                    results[
                        robot_index
                    ][scenario].append(
                        recording_minimum
                    )

                    print(
                        f"Session {session}, "
                        f"Scenario {scenario}, "
                        f"Robot {robot_index}: "
                        f"{recording_minimum:.3f} m"
                    )

            except Exception as exc:

                print(
                    f"[WARNING] Could not process "
                    f"session={session}, "
                    f"scenario={scenario}: "
                    f"{exc}"
                )

    return results



def plot_scenario_distribution(
    results,
    robot_number,
):
    """
    Plot recording-level minimum distances across scenarios.
    """

    data = [
        results[robot_number][scenario]
        for scenario in SCENARIOS
    ]

    labels = [
        f"Scenario {scenario}"
        for scenario in SCENARIOS
    ]

    fig, ax = plt.subplots(
        figsize=(6.4, 3.8)
    )

    ax.boxplot(
        data,
        labels=labels,
        widths=0.55,
        showfliers=False,
    )

   
    rng = np.random.default_rng(42)

    for idx, values in enumerate(
        data,
        start=1,
    ):

        if not values:
            continue

        x = (
            idx
            + rng.uniform(
                -0.08,
                0.08,
                size=len(values),
            )
        )

        ax.scatter(
            x,
            values,
            s=18,
            alpha=0.65,
            zorder=3,
        )

    ax.set_xlabel("Scenario")

    ax.set_ylabel(
        "Minimum human–robot distance (m)"
    )

    ax.set_title(
        f"Robot {robot_number}"
    )

    ax.grid(
        axis="y",
        linestyle=":",
        linewidth=0.6,
        alpha=0.6,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    filename = (
        f"min_human_robot_distance_"
        f"robot{robot_number}_by_scenario"
    )

    png_path = OUTPUT / f"{filename}.png"
    pdf_path = OUTPUT / f"{filename}.pdf"

    fig.savefig(
        png_path,
        dpi=300,
        bbox_inches="tight",
    )

    fig.savefig(
        pdf_path,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


def main():

    solved_loader = DatasetLoader(
        root=ROOT_SOLVED,
        config=CONFIG,
    )

    raw_loader = DatasetLoader(
        root=ROOT_RAW,
        config=CONFIG,
    )


    print()
    print("=" * 70)
    print("TIME-SERIES FIGURES")
    print("=" * 70)

    for scenario in SCENARIOS:

        print(
            f"\nScenario {scenario}, "
            f"Session {REPRESENTATIVE_SESSION}"
        )

        try:

            solved_df, info = load_recording(
                solved_loader,
                raw_loader,
                REPRESENTATIVE_SESSION,
                scenario,
            )

            robots = info["robots"]

            if len(robots) < 2:
                print(
                    f"[WARNING] Only {len(robots)} "
                    f"robot(s) found."
                )
                continue

            for robot_index, robot in enumerate(
                robots[:2],
                start=1,
            ):

                print(
                    f"  Robot {robot_index}: "
                    f"{robot}"
                )

                time, distance = (
                    compute_min_human_robot_distance(
                        df=solved_df,
                        robot=robot,
                        humans=info["humans"],
                        frame_rate=FRAME_RATE,
                    )
                )

                valid = np.isfinite(distance)

                time = time[valid]
                distance = distance[valid]

                print(
                    f"    Mean   : "
                    f"{np.mean(distance):.3f} m"
                )

                print(
                    f"    Median : "
                    f"{np.median(distance):.3f} m"
                )

                print(
                    f"    Minimum: "
                    f"{np.min(distance):.3f} m"
                )

                print(
                    f"    Maximum: "
                    f"{np.max(distance):.3f} m"
                )

                plot_time_series(
                    time=time,
                    distance=distance,
                    session=REPRESENTATIVE_SESSION,
                    scenario=scenario,
                    robot_number=robot_index,
                )

        except Exception as exc:

            print(
                f"[WARNING] Could not generate "
                f"Scenario {scenario}: {exc}"
            )

    print()
    print("=" * 70)
    print("RECORDING-LEVEL DISTRIBUTIONS")
    print("=" * 70)

    results = collect_recording_minima(
        solved_loader,
        raw_loader,
    )

    print()
    print("Summary")
    print("-" * 70)

    for robot_number in [1, 2]:

        print()
        print(f"Robot {robot_number}")

        for scenario in SCENARIOS:

            values = np.asarray(
                results[robot_number][scenario],
                dtype=float,
            )

            if len(values) == 0:
                continue

            print(
                f"  Scenario {scenario}: "
                f"n={len(values)}, "
                f"mean={np.mean(values):.3f} m, "
                f"median={np.median(values):.3f} m, "
                f"min={np.min(values):.3f} m"
            )

  
    plot_scenario_distribution(
        results,
        robot_number=1,
    )

    plot_scenario_distribution(
        results,
        robot_number=2,
    )

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()