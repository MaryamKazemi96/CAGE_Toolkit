# """
# Produce ONE standalone, camera-ready figure per statistical test (as
# opposed to combining multiple tests into a single multi-panel figure).

# Generates, each as its own .png + .pdf:
#   - fig_paired_<label>              (one per ITEM_PAIRS entry: implicit
#                                       vs explicit boxplot + significance
#                                       bracket)
#   - fig_tlx_density                 (NASA-TLX by crowd density, KDE)
#   - fig_preference_post_s3          (preference bar chart after Scenario 3)
#   - fig_preference_final            (preference bar chart, final)

# Usage
# -----
#     python scripts/make_survey_paper_figures.py
# """

# from __future__ import annotations

# from pathlib import Path

# import matplotlib.pyplot as plt

# from src.survey.data import load_survey, ITEM_PAIRS
# from src.survey.stats import run_all_item_pair_tests
# from src.survey.plots import plot_paired_comparison, plot_tlx_density_kde, plot_preference_bar

# # ---------------------------------------------------------------------

# INPUT_CSV = Path("data/survey/survey.csv")

# OUTPUT = Path("results/paper_figures")
# OUTPUT.mkdir(parents=True, exist_ok=True)

# # Paper-figure sizing -- tuned for a single-column IEEE/ICRA-style figure.
# plt.rcParams.update({
#     "font.size": 10,
#     "axes.titlesize": 11,
#     "axes.labelsize": 10,
#     "figure.dpi": 300,
# })


# def save(fig, name: str) -> None:

#     out_base = OUTPUT / name
#     fig.savefig(out_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
#     fig.savefig(out_base.with_suffix(".pdf"), bbox_inches="tight")
#     plt.close(fig)

#     print(f"Saved: {out_base.with_suffix('.png').resolve()}")
#     print(f"Saved: {out_base.with_suffix('.pdf').resolve()}")


# def make_paired_figures(df) -> None:
#     """One standalone figure per ITEM_PAIRS entry, with significance bracket."""

#     pair_results = run_all_item_pair_tests(df)

#     for pair, res in zip(ITEM_PAIRS, pair_results):

#         p_for_plot = res.get("wilcoxon_p", res.get("paired_t_p"))

#         fig, ax = plt.subplots(figsize=(4.5, 5))
#         plot_paired_comparison(df, pair, ax=ax, paper_style=True, p_value=p_for_plot)
#         fig.tight_layout()

#         slug = pair["label"].lower().replace(" ", "_").replace("/", "-")
#         save(fig, f"fig_paired_{slug}")


# def make_tlx_density_figure(df) -> None:

#     fig, ax = plt.subplots(figsize=(6, 4.2))
#     plot_tlx_density_kde(df, ax=ax, paper_style=True)
#     ax.set_title("NASA-TLX workload by crowd density", fontsize=11)
#     fig.tight_layout()

#     save(fig, "fig_tlx_density")


# def make_preference_figures(df) -> None:

#     fig, ax = plt.subplots(figsize=(4.5, 4))
#     plot_preference_bar(df, "PostS3_Q5_S3Preference", "Preference after Scenario 3 (implicit)", ax=ax, paper_style=True)
#     fig.tight_layout()
#     save(fig, "fig_preference_post_s3")

#     fig, ax = plt.subplots(figsize=(4.5, 4))
#     plot_preference_bar(df, "PostS4_Q5_FinalPreference", "Final preference (after Scenario 4 / explicit)", ax=ax, paper_style=True)
#     fig.tight_layout()
#     save(fig, "fig_preference_final")


# def main() -> None:

#     df = load_survey(INPUT_CSV, verbose=False)

#     make_paired_figures(df)
#     make_tlx_density_figure(df)
#     make_preference_figures(df)

#     print(f"\nDone. Figures saved to: {OUTPUT.resolve()}")


# if __name__ == "__main__":
#     main()




"""
Produce ONE standalone, camera-ready figure per statistical test (as
opposed to combining multiple tests into a single multi-panel figure).

Generates, each as its own .png + .pdf:
  - fig_related_<construct>   (one per RELATED_ITEM_GROUPS entry: implicit
                                and explicit items shown side-by-side,
                                each with its OWN independent one-sample
                                mean/CI/p-value -- NOT a paired test, since
                                the two items use different wording)
  - fig_tlx_density            (NASA-TLX by crowd density, KDE)
  - fig_preference_post_s3     (preference bar chart after Scenario 3)
  - fig_preference_final       (preference bar chart, final)

Usage
-----
    python scripts/make_survey_paper_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from src.survey.data import load_survey, RELATED_ITEM_GROUPS
from src.survey.stats import run_related_group_tests
from src.survey.plots import plot_related_group_bars, plot_tlx_density_kde, plot_preference_bar

# ---------------------------------------------------------------------

INPUT_CSV = Path("data/survey/survey.csv")

OUTPUT = Path("results/paper_figures")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Paper-figure sizing -- tuned for a single-column IEEE/ICRA-style figure.
plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "figure.dpi": 300,
})


def save(fig, name: str) -> None:

    out_base = OUTPUT / name
    fig.savefig(out_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(out_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {out_base.with_suffix('.png').resolve()}")
    print(f"Saved: {out_base.with_suffix('.pdf').resolve()}")


def make_related_group_figures(df) -> None:
    """One standalone figure per RELATED_ITEM_GROUPS entry -- independent bars, no bracket."""

    group_results = run_related_group_tests(df)

    for gres in group_results:

        fig, ax = plt.subplots(figsize=(4.5, 5))
        plot_related_group_bars(gres, ax=ax, paper_style=True)
        fig.tight_layout()

        slug = gres["group_meta"]["construct"].lower().replace(" ", "_").replace("/", "-")
        save(fig, f"fig_related_{slug}")


def make_tlx_density_figure(df) -> None:

    fig, ax = plt.subplots(figsize=(6, 4.2))
    plot_tlx_density_kde(df, ax=ax, paper_style=True)
    ax.set_title("NASA-TLX workload by crowd density", fontsize=11)
    fig.tight_layout()

    save(fig, "fig_tlx_density")


def make_preference_figures(df) -> None:

    fig, ax = plt.subplots(figsize=(4.5, 4))
    plot_preference_bar(df, "PostS3_Q5_S3Preference", "Preference after Scenario 3 (implicit)", ax=ax, paper_style=True)
    fig.tight_layout()
    save(fig, "fig_preference_post_s3")

    fig, ax = plt.subplots(figsize=(4.5, 4))
    plot_preference_bar(df, "PostS4_Q5_FinalPreference", "Final preference (after Scenario 4 / explicit)", ax=ax, paper_style=True)
    fig.tight_layout()
    save(fig, "fig_preference_final")


def main() -> None:

    df = load_survey(INPUT_CSV, verbose=False)

    make_related_group_figures(df)
    make_tlx_density_figure(df)
    make_preference_figures(df)

    print(f"\nDone. Figures saved to: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()