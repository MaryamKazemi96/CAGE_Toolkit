# """
# Plotting functions for the survey analysis. Each function draws onto a
# given `ax` (or creates one if ax=None) and returns (fig, ax), following
# the same convention as src/visualization/plot.py, so figures can be
# composed into multi-panel layouts by callers.
# """

# from __future__ import annotations

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy import stats

# from src.survey.data import PREFERENCE_LABELS


# def _p_to_stars(p: float) -> str:
#     if p < 0.001:
#         return "***"
#     if p < 0.01:
#         return "**"
#     if p < 0.05:
#         return "*"
#     return "n.s."


# def plot_paired_comparison(df, pair, ax=None, paper_style=False, p_value=None):
#     """
#     Boxplot of one ITEM_PAIRS entry: implicit (S3) vs explicit (S4).

#     paper_style : if True, uses larger fonts / tighter layout suited for
#     a print figure rather than a quick exploratory plot.
#     p_value : if given, draws a significance bracket + asterisks (or
#     "n.s.") above the two boxes, using the standard * p<.05, ** p<.01,
#     *** p<.001 convention.
#     """

#     if ax is None:
#         fig, ax = plt.subplots(figsize=(4.5, 5))
#     else:
#         fig = ax.figure

#     col_a = pair["col_implicit"]
#     col_b = pair["col_explicit_used"]

#     sub = df[[col_a, col_b]].dropna()

#     fontsize = 11 if paper_style else 9

#     ax.boxplot(
#         [sub[col_a], sub[col_b]],
#         labels=["Implicit (S3)", "Explicit (S4)"],
#         widths=0.5,
#         patch_artist=True,
#         boxprops=dict(facecolor="#a6cee3"),
#         medianprops=dict(color="black"),
#     )

#     # overlay individual points with slight jitter for transparency
#     rng = np.random.default_rng(0)
#     for i, col in enumerate([col_a, col_b], start=1):
#         jitter = rng.uniform(-0.08, 0.08, size=len(sub))
#         ax.scatter(np.full(len(sub), i) + jitter, sub[col], color="black", alpha=0.35, s=14, zorder=3)

#     if p_value is not None:

#         y_max = max(sub[col_a].max(), sub[col_b].max())
#         y_range = y_max - min(sub[col_a].min(), sub[col_b].min())
#         bracket_y = y_max + 0.08 * max(y_range, 1)
#         tick_h = 0.02 * max(y_range, 1)

#         ax.plot(
#             [1, 1, 2, 2],
#             [bracket_y, bracket_y + tick_h, bracket_y + tick_h, bracket_y],
#             color="black", lw=1,
#         )
#         ax.text(
#             1.5, bracket_y + tick_h * 1.3, _p_to_stars(p_value),
#             ha="center", va="bottom", fontsize=fontsize,
#         )
#         ax.set_ylim(top=bracket_y + tick_h * 4)

#     ax.set_ylabel(pair["polarity"].capitalize(), fontsize=fontsize)
#     ax.set_title(pair["label"], fontsize=fontsize + 1)
#     ax.tick_params(axis="both", labelsize=fontsize - 1)
#     ax.grid(axis="y", alpha=0.3)

#     return fig, ax


# def plot_effect_size_summary(pair_results, tlx_result=None, ax=None, paper_style=False):
#     """
#     Forest-plot-style summary of effect sizes (Cohen's d, with an
#     approximate 95% CI) across all paired implicit-vs-explicit
#     comparisons, plus the TLX-by-density independent-groups comparison
#     if given. One row per test; vertical line at d=0 (no effect).

#     pair_results : list of dicts from src.survey.stats.run_all_item_pair_tests()
#     tlx_result : optional dict from src.survey.stats.tlx_density_test()
#     """

#     import numpy as np

#     if ax is None:
#         fig, ax = plt.subplots(figsize=(7, 0.9 * (len(pair_results) + (1 if tlx_result else 0)) + 1.5))
#     else:
#         fig = ax.figure

#     fontsize = 11 if paper_style else 9

#     rows = []  # (label, d, ci_low, ci_high, p)

#     for res in pair_results:

#         if "cohens_d" not in res:
#             continue

#         n = res["n_pairs"]
#         d = res["cohens_d"]
#         # approximate SE of Cohen's d for paired samples
#         se = np.sqrt(1.0 / n + d ** 2 / (2 * n))
#         ci = 1.96 * se

#         p = res.get("wilcoxon_p", res.get("paired_t_p"))

#         rows.append((res["pair_meta"]["label"], d, d - ci, d + ci, p))

#     if tlx_result is not None and "welch_t" in tlx_result:

#         n1, n2 = tlx_result["n_low"], tlx_result["n_high"]
#         # Cohen's d for independent groups, from Welch's t as an approximation
#         d = tlx_result["welch_t"] * np.sqrt(1 / n1 + 1 / n2)
#         se = np.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
#         ci = 1.96 * se
#         p = tlx_result.get("mannwhitney_p", tlx_result.get("welch_p"))

#         rows.append(("NASA-TLX: low vs. high density", d, d - ci, d + ci, p))

#     ys = np.arange(len(rows))[::-1]

#     for y, (label, d, lo, hi, p) in zip(ys, rows):

#         color = "tab:red" if (p is not None and p < 0.05) else "tab:gray"

#         ax.plot([lo, hi], [y, y], color=color, lw=2)
#         ax.plot(d, y, "o", color=color, markersize=8)

#         marker = _p_to_stars(p) if p is not None else ""
#         ax.text(
#             hi + 0.05, y, f"d={d:.2f}  {marker}",
#             va="center", fontsize=fontsize - 1,
#         )

#     ax.axvline(0, color="black", lw=1, linestyle="--")

#     ax.set_yticks(ys)
#     ax.set_yticklabels([r[0] for r in rows], fontsize=fontsize)
#     ax.set_xlabel("Effect size (Cohen's d)\n(implicit \u2212 explicit / low \u2212 high density)", fontsize=fontsize)
#     ax.set_title("Summary of statistical tests", fontsize=fontsize + 1)
#     ax.grid(axis="x", alpha=0.3)

#     # give room for the annotation text on the right
#     xmax = max(r[3] for r in rows) if rows else 1
#     xmin = min(r[2] for r in rows) if rows else -1
#     ax.set_xlim(xmin - 0.2, xmax + 0.9)

#     return fig, ax


# def plot_tlx_density_kde(df, ax=None, paper_style=False):
#     """KDE overlay of NASA-TLX workload distribution, low vs high density."""

#     if ax is None:
#         fig, ax = plt.subplots(figsize=(7, 4.5))
#     else:
#         fig = ax.figure

#     low = df.loc[df["density"] == "low", "TLX_recomputed"].dropna()
#     high = df.loc[df["density"] == "high", "TLX_recomputed"].dropna()

#     fontsize = 11 if paper_style else 9

#     for label, group, color in [("Low density", low, "tab:blue"), ("High density", high, "tab:red")]:
#         if len(group) >= 2:
#             kde = stats.gaussian_kde(group)
#             xs = np.linspace(max(group.min() - 2, 0), group.max() + 2, 200)
#             ax.plot(xs, kde(xs), color=color, label=f"{label} (n={len(group)})", lw=2)
#             ax.fill_between(xs, kde(xs), alpha=0.2, color=color)

#     ax.set_xlabel("NASA-TLX workload score", fontsize=fontsize)
#     ax.set_ylabel("Density", fontsize=fontsize)
#     if not paper_style:
#         ax.set_title("Perceived workload distribution by crowd density", fontsize=fontsize + 1)
#     ax.tick_params(axis="both", labelsize=fontsize - 1)
#     ax.legend(fontsize=fontsize - 1)
#     ax.grid(alpha=0.3)

#     return fig, ax


# def plot_preference_bar(df, col, title, ax=None, paper_style=False):
#     """Bar chart of a categorical preference column's frequency."""

#     if ax is None:
#         fig, ax = plt.subplots(figsize=(6, 4))
#     else:
#         fig = ax.figure

#     counts = df[col].dropna().map(PREFERENCE_LABELS).value_counts()
#     counts = counts.reindex(PREFERENCE_LABELS.values(), fill_value=0)

#     fontsize = 11 if paper_style else 9

#     ax.bar(counts.index, counts.to_numpy(), color="#1f78b4")
#     ax.set_ylabel("Number of participants", fontsize=fontsize)
#     ax.set_title(title, fontsize=fontsize + 1)
#     ax.tick_params(axis="x", rotation=20, labelsize=fontsize - 1)
#     ax.tick_params(axis="y", labelsize=fontsize - 1)
#     ax.grid(axis="y", alpha=0.3)

#     return fig, ax


# def plot_item_diagnostic(one_sample_result: dict, title: str, ylabel: str = "Rating"):
#     """
#     4-panel diagnostic figure for a single item's one-sample test against
#     a reference value, matching the "Reduced Anxiety" style: mean+CI bar,
#     box+jittered points, violin, and histogram+density -- each with the
#     reference line marked, and the mean/p-value annotated.

#     one_sample_result : dict from src.survey.stats.one_sample_test()
#     """

#     values = one_sample_result["values"]
#     reference = one_sample_result["reference"]
#     mean = one_sample_result["mean"]

#     p = one_sample_result.get("wilcoxon_p", one_sample_result.get("t_p"))

#     fig, axes = plt.subplots(2, 2, figsize=(11, 9))
#     fig.suptitle(title, fontsize=14)

#     # --- (top-left) mean bar with 95% CI ---------------------------------

#     ax = axes[0, 0]
#     ax.bar(["Condition"], [mean], color="tab:blue", width=0.6)

#     if "ci_low" in one_sample_result:
#         ax.errorbar(
#             ["Condition"], [mean],
#             yerr=[[mean - one_sample_result["ci_low"]], [one_sample_result["ci_high"] - mean]],
#             fmt="none", ecolor="black", capsize=6, lw=1.5,
#         )

#     ax.axhline(reference, color="red", linestyle="--", lw=1.5)
#     ax.set_ylim(1, 5)
#     ax.set_title("Mean Rating with 95% CI")

#     label = f"M={mean:.2f}"
#     if p is not None:
#         label += f"\np={p:.3f}"
#     ax.text(0, mean + 0.15, label, ha="center", va="bottom", fontsize=11)

#     # --- (top-right) box + individual points -----------------------------

#     ax = axes[0, 1]
#     ax.boxplot(values, vert=False, widths=0.5, positions=[1], patch_artist=True,
#                boxprops=dict(facecolor="0.9"), medianprops=dict(color="black"))

#     rng = np.random.default_rng(0)
#     jitter = rng.uniform(-0.15, 0.15, size=len(values))
#     ax.scatter(values, np.ones(len(values)) + jitter, color="black", alpha=0.5, s=25, zorder=3)

#     ax.axvline(reference, color="red", linestyle="--", lw=1.5)
#     ax.set_yticks([])
#     ax.set_xlim(0.5, 5.5)
#     ax.set_xlabel(ylabel)
#     ax.set_title("Distribution (Box + Individual Points)")

#     # --- (bottom-left) violin ----------------------------------------------

#     ax = axes[1, 0]
#     parts = ax.violinplot(values, showmedians=False, showextrema=False)
#     for pc in parts["bodies"]:
#         pc.set_facecolor("#a6cee3")
#         pc.set_edgecolor("black")
#         pc.set_alpha(0.8)

#     ax.boxplot(values, widths=0.08, patch_artist=True,
#                boxprops=dict(facecolor="0.4"), medianprops=dict(color="white"),
#                whiskerprops=dict(color="black"), capprops=dict(color="black"))

#     ax.axhline(reference, color="red", linestyle="--", lw=1.5)
#     ax.set_ylim(0, 6)
#     ax.set_ylabel(ylabel)
#     ax.set_xticks([])
#     ax.set_title("Distribution Shape (Violin Plot)")

#     # --- (bottom-right) histogram + density ---------------------------------

#     ax = axes[1, 1]
#     bins = np.arange(0.75, 5.75, 0.5)
#     ax.hist(values, bins=bins, color="0.75", edgecolor="0.4")

#     if len(np.unique(values)) > 1:
#         kde = stats.gaussian_kde(values)
#         xs = np.linspace(1, 5, 200)
#         # scale KDE to roughly match histogram counts for visual overlay
#         scale = len(values) * 0.5
#         ax.plot(xs, kde(xs) * scale, color="0.3", lw=1.5)

#     ax.axvline(reference, color="red", linestyle="--", lw=1.5, label=f"Neutral ({reference:.0f})")
#     ax.axvline(mean, color="blue", lw=1.5, label=f"Mean ({mean:.2f})")
#     ax.set_xlabel(ylabel)
#     ax.set_ylabel("Count")
#     ax.set_title("Histogram + Density")
#     ax.legend(fontsize=8)

#     fig.tight_layout()

#     return fig, axes




"""
Plotting functions for the survey analysis. Each function draws onto a
given `ax` (or creates one if ax=None) and returns (fig, ax), following
the same convention as src/visualization/plot.py, so figures can be
composed into multi-panel layouts by callers.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from src.survey.data import PREFERENCE_LABELS


def _p_to_stars(p: float) -> str:
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def plot_paired_comparison(df, pair, ax=None, paper_style=False, p_value=None):
    """
    Boxplot of one ITEM_PAIRS entry: implicit (S3) vs explicit (S4).

    paper_style : if True, uses larger fonts / tighter layout suited for
    a print figure rather than a quick exploratory plot.
    p_value : if given, draws a significance bracket + asterisks (or
    "n.s.") above the two boxes, using the standard * p<.05, ** p<.01,
    *** p<.001 convention.
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(4.5, 5))
    else:
        fig = ax.figure

    col_a = pair["col_implicit"]
    col_b = pair["col_explicit_used"]

    sub = df[[col_a, col_b]].dropna()

    fontsize = 11 if paper_style else 9

    ax.boxplot(
        [sub[col_a], sub[col_b]],
        labels=["Implicit (S3)", "Explicit (S4)"],
        widths=0.5,
        patch_artist=True,
        boxprops=dict(facecolor="#a6cee3"),
        medianprops=dict(color="black"),
    )

    # overlay individual points with slight jitter for transparency
    rng = np.random.default_rng(0)
    for i, col in enumerate([col_a, col_b], start=1):
        jitter = rng.uniform(-0.08, 0.08, size=len(sub))
        ax.scatter(np.full(len(sub), i) + jitter, sub[col], color="black", alpha=0.35, s=14, zorder=3)

    if p_value is not None:

        y_max = max(sub[col_a].max(), sub[col_b].max())
        y_range = y_max - min(sub[col_a].min(), sub[col_b].min())
        bracket_y = y_max + 0.08 * max(y_range, 1)
        tick_h = 0.02 * max(y_range, 1)

        ax.plot(
            [1, 1, 2, 2],
            [bracket_y, bracket_y + tick_h, bracket_y + tick_h, bracket_y],
            color="black", lw=1,
        )
        ax.text(
            1.5, bracket_y + tick_h * 1.3, _p_to_stars(p_value),
            ha="center", va="bottom", fontsize=fontsize,
        )
        ax.set_ylim(top=bracket_y + tick_h * 4)

    ax.set_ylabel(pair["polarity"].capitalize(), fontsize=fontsize)
    ax.set_title(pair["label"], fontsize=fontsize + 1)
    ax.tick_params(axis="both", labelsize=fontsize - 1)
    ax.grid(axis="y", alpha=0.3)

    return fig, ax


def plot_effect_size_summary(pair_results, tlx_result=None, ax=None, paper_style=False):
    """
    Forest-plot-style summary of effect sizes (Cohen's d, with an
    approximate 95% CI) across all paired implicit-vs-explicit
    comparisons, plus the TLX-by-density independent-groups comparison
    if given. One row per test; vertical line at d=0 (no effect).

    pair_results : list of dicts from src.survey.stats.run_all_item_pair_tests()
    tlx_result : optional dict from src.survey.stats.tlx_density_test()
    """

    import numpy as np

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 0.9 * (len(pair_results) + (1 if tlx_result else 0)) + 1.5))
    else:
        fig = ax.figure

    fontsize = 11 if paper_style else 9

    rows = []  # (label, d, ci_low, ci_high, p)

    for res in pair_results:

        if "cohens_d" not in res:
            continue

        n = res["n_pairs"]
        d = res["cohens_d"]
        # approximate SE of Cohen's d for paired samples
        se = np.sqrt(1.0 / n + d ** 2 / (2 * n))
        ci = 1.96 * se

        p = res.get("wilcoxon_p", res.get("paired_t_p"))

        rows.append((res["pair_meta"]["label"], d, d - ci, d + ci, p))

    if tlx_result is not None and "welch_t" in tlx_result:

        n1, n2 = tlx_result["n_low"], tlx_result["n_high"]
        # Cohen's d for independent groups, from Welch's t as an approximation
        d = tlx_result["welch_t"] * np.sqrt(1 / n1 + 1 / n2)
        se = np.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
        ci = 1.96 * se
        p = tlx_result.get("mannwhitney_p", tlx_result.get("welch_p"))

        rows.append(("NASA-TLX: low vs. high density", d, d - ci, d + ci, p))

    ys = np.arange(len(rows))[::-1]

    for y, (label, d, lo, hi, p) in zip(ys, rows):

        color = "tab:red" if (p is not None and p < 0.05) else "tab:gray"

        ax.plot([lo, hi], [y, y], color=color, lw=2)
        ax.plot(d, y, "o", color=color, markersize=8)

        marker = _p_to_stars(p) if p is not None else ""
        ax.text(
            hi + 0.05, y, f"d={d:.2f}  {marker}",
            va="center", fontsize=fontsize - 1,
        )

    ax.axvline(0, color="black", lw=1, linestyle="--")

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=fontsize)
    ax.set_xlabel("Effect size (Cohen's d)\n(implicit \u2212 explicit / low \u2212 high density)", fontsize=fontsize)
    ax.set_title("Summary of statistical tests", fontsize=fontsize + 1)
    ax.grid(axis="x", alpha=0.3)

    # give room for the annotation text on the right
    xmax = max(r[3] for r in rows) if rows else 1
    xmin = min(r[2] for r in rows) if rows else -1
    ax.set_xlim(xmin - 0.2, xmax + 0.9)

    return fig, ax


def plot_tlx_density_kde(df, ax=None, paper_style=False):
    """KDE overlay of NASA-TLX workload distribution, low vs high density."""

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4.5))
    else:
        fig = ax.figure

    low = df.loc[df["density"] == "low", "TLX_recomputed"].dropna()
    high = df.loc[df["density"] == "high", "TLX_recomputed"].dropna()

    fontsize = 11 if paper_style else 9

    for label, group, color in [("Low density", low, "tab:blue"), ("High density", high, "tab:red")]:
        if len(group) >= 2:
            kde = stats.gaussian_kde(group)
            xs = np.linspace(max(group.min() - 2, 0), group.max() + 2, 200)
            ax.plot(xs, kde(xs), color=color, label=f"{label} (n={len(group)})", lw=2)
            ax.fill_between(xs, kde(xs), alpha=0.2, color=color)

    ax.set_xlabel("NASA-TLX workload score", fontsize=fontsize)
    ax.set_ylabel("Density", fontsize=fontsize)
    if not paper_style:
        ax.set_title("Perceived workload distribution by crowd density", fontsize=fontsize + 1)
    ax.tick_params(axis="both", labelsize=fontsize - 1)
    ax.legend(fontsize=fontsize - 1)
    ax.grid(alpha=0.3)

    return fig, ax


def plot_preference_bar(df, col, title, ax=None, paper_style=False):
    """Bar chart of a categorical preference column's frequency."""

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.figure

    counts = df[col].dropna().map(PREFERENCE_LABELS).value_counts()
    counts = counts.reindex(PREFERENCE_LABELS.values(), fill_value=0)

    fontsize = 11 if paper_style else 9

    ax.bar(counts.index, counts.to_numpy(), color="#1f78b4")
    ax.set_ylabel("Number of participants", fontsize=fontsize)
    ax.set_title(title, fontsize=fontsize + 1)
    ax.tick_params(axis="x", rotation=20, labelsize=fontsize - 1)
    ax.tick_params(axis="y", labelsize=fontsize - 1)
    ax.grid(axis="y", alpha=0.3)

    return fig, ax


def plot_item_diagnostic(one_sample_result: dict, title: str, ylabel: str = "Rating"):
    """
    4-panel diagnostic figure for a single item's one-sample test against
    a reference value, matching the "Reduced Anxiety" style: mean+CI bar,
    box+jittered points, violin, and histogram+density -- each with the
    reference line marked, and the mean/p-value annotated.

    one_sample_result : dict from src.survey.stats.one_sample_test()
    """

    values = one_sample_result["values"]
    reference = one_sample_result["reference"]
    mean = one_sample_result["mean"]

    p = one_sample_result.get("wilcoxon_p", one_sample_result.get("t_p"))

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    fig.suptitle(title, fontsize=14)

    # --- (top-left) mean bar with 95% CI ---------------------------------

    ax = axes[0, 0]
    ax.bar(["Condition"], [mean], color="tab:blue", width=0.6)

    if "ci_low" in one_sample_result:
        ax.errorbar(
            ["Condition"], [mean],
            yerr=[[mean - one_sample_result["ci_low"]], [one_sample_result["ci_high"] - mean]],
            fmt="none", ecolor="black", capsize=6, lw=1.5,
        )

    ax.axhline(reference, color="red", linestyle="--", lw=1.5)
    ax.set_ylim(1, 5)
    ax.set_title("Mean Rating with 95% CI")

    label = f"M={mean:.2f}"
    if p is not None:
        label += f"\np={p:.3f}"
    ax.text(0, mean + 0.15, label, ha="center", va="bottom", fontsize=11)

    # --- (top-right) box + individual points -----------------------------

    ax = axes[0, 1]
    ax.boxplot(values, vert=False, widths=0.5, positions=[1], patch_artist=True,
               boxprops=dict(facecolor="0.9"), medianprops=dict(color="black"))

    rng = np.random.default_rng(0)
    jitter = rng.uniform(-0.15, 0.15, size=len(values))
    ax.scatter(values, np.ones(len(values)) + jitter, color="black", alpha=0.5, s=25, zorder=3)

    ax.axvline(reference, color="red", linestyle="--", lw=1.5)
    ax.set_yticks([])
    ax.set_xlim(0.5, 5.5)
    ax.set_xlabel(ylabel)
    ax.set_title("Distribution (Box + Individual Points)")

    # --- (bottom-left) violin ----------------------------------------------

    ax = axes[1, 0]
    parts = ax.violinplot(values, showmedians=False, showextrema=False)
    for pc in parts["bodies"]:
        pc.set_facecolor("#a6cee3")
        pc.set_edgecolor("black")
        pc.set_alpha(0.8)

    ax.boxplot(values, widths=0.08, patch_artist=True,
               boxprops=dict(facecolor="0.4"), medianprops=dict(color="white"),
               whiskerprops=dict(color="black"), capprops=dict(color="black"))

    ax.axhline(reference, color="red", linestyle="--", lw=1.5)
    ax.set_ylim(0, 6)
    ax.set_ylabel(ylabel)
    ax.set_xticks([])
    ax.set_title("Distribution Shape (Violin Plot)")

    # --- (bottom-right) histogram + density ---------------------------------

    ax = axes[1, 1]
    bins = np.arange(0.75, 5.75, 0.5)
    ax.hist(values, bins=bins, color="0.75", edgecolor="0.4")

    if len(np.unique(values)) > 1:
        kde = stats.gaussian_kde(values)
        xs = np.linspace(1, 5, 200)
        # scale KDE to roughly match histogram counts for visual overlay
        scale = len(values) * 0.5
        ax.plot(xs, kde(xs) * scale, color="0.3", lw=1.5)

    ax.axvline(reference, color="red", linestyle="--", lw=1.5, label=f"Neutral ({reference:.0f})")
    ax.axvline(mean, color="blue", lw=1.5, label=f"Mean ({mean:.2f})")
    ax.set_xlabel(ylabel)
    ax.set_ylabel("Count")
    ax.set_title("Histogram + Density")
    ax.legend(fontsize=8)

    fig.tight_layout()

    return fig, axes


def plot_related_group_bars(group_result: dict, ax=None, paper_style=False, reference: float = 3.0):


    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))
    else:
        fig = ax.figure

    meta = group_result["group_meta"]
    sides = [("implicit", group_result["implicit"]), ("explicit", group_result["explicit"])]

    fontsize = 11 if paper_style else 9

    means = []
    for i, (key, res) in enumerate(sides):

        mean = res["mean"]
        means.append(mean)

        ax.bar(i, mean, width=0.6, color="tab:blue" if key == "implicit" else "tab:orange")

        if "ci_low" in res:
            ax.errorbar(
                i, mean,
                yerr=[[mean - res["ci_low"]], [res["ci_high"] - mean]],
                fmt="none", ecolor="black", capsize=6, lw=1.5,
            )

        p = res.get("wilcoxon_p", res.get("t_p"))
        star = _p_to_stars(p) if p is not None else ""

        label = f"M={mean:.2f}"
        if p is not None:
            label += f"\np={p:.3f} {star}"

        ax.text(i, mean + 0.15, label, ha="center", va="bottom", fontsize=fontsize - 1)

    ax.axhline(reference, color="red", linestyle="--", lw=1.5)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(
        [meta["implicit"]["label"], meta["explicit"]["label"]],
        fontsize=fontsize,
    )
    ax.set_ylim(1, 5)
    ax.set_ylabel("Rating", fontsize=fontsize)
    ax.set_title(meta["construct"], fontsize=fontsize + 1)
    ax.grid(axis="y", alpha=0.3)

    return fig, ax

def plot_preference_transition(pref_res):

    import matplotlib.pyplot as plt
    import seaborn as sns

    transition = pref_res["transition"].copy()

    labels = [
        "Base robot",
        "Delivery robot",
        "Equally easy",
        "Equally difficult",
    ]

    transition.index = labels
    transition.columns = labels

    fig, ax = plt.subplots(figsize=(6, 5))

    sns.heatmap(
        transition,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        linewidths=0.5,
        ax=ax,
    )

    ax.set_xlabel("Scenario 4: Explicit intent")
    ax.set_ylabel("Scenario 3: Implicit intent")

    plt.tight_layout()

    fig.savefig(
        "results/survey_analysis/plots/preference_s3_vs_s4.pdf",
        format="pdf",
        bbox_inches="tight",
    )

    return fig, ax


def plot_preference_transitionold(pref_res):

    import matplotlib.pyplot as plt
    import seaborn as sns

    transition = pref_res["transition"].copy()

    labels = [
        "Base robot",
        "Delivery robot",
        "Equally easy",
        "Equally difficult",
    ]

    transition.index = labels
    transition.columns = labels

    fig, ax = plt.subplots(figsize=(6, 5))

    sns.heatmap(
        transition,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        linewidths=0.5,
        ax=ax,
    )

    ax.set_xlabel("Scenario 4: Explicit intent")
    ax.set_ylabel("Scenario 3: Implicit intent")
    ax.set_title("Preference transitions")

    plt.tight_layout()

    return fig, ax

def plot_explicit_intent_likert(df):

    import matplotlib.pyplot as plt
    import numpy as np

    questions = {
        "Destination clarity": "PostS4_Q1_ProjClarity",
        "Earlier path alteration": "PostS4_Q3_EarlyPathAlter",
        "Perceived safety": "PostS4_Q4_ReducedAnxiety",
    }

    # Likert scale: 1 = negative, 3 = neutral, 5 = positive
    likert_values = [1, 2, 3, 4, 5]

    response_labels = ["1", "2", "3", "4", "5"]

    palette = [
        "#DCEAF7",  # 1
        "#A9CBE8",  # 2
        "#E5E5E5",  # 3 (neutral)
        "#6FA8DC",  # 4
        "#1F5A94",  # 5
    ]

    distributions = []

    for label, column in questions.items():
        values = df[column].dropna()

        counts = (
            values
            .value_counts()
            .reindex(likert_values, fill_value=0)
        )

        percentages = counts / counts.sum() * 100

        distributions.append(
            (label, percentages.to_numpy())
        )

    fig, ax = plt.subplots(figsize=(7.0, 2.8))

    y = np.arange(len(distributions))

    left = np.zeros(len(distributions))

    for i, value in enumerate(likert_values):

        widths = np.array([
            distribution[1][i]
            for distribution in distributions
        ])

        ax.barh(
            y,
            widths,
            left=left,
            height=0.55,
            color=palette[i],
            edgecolor="white",
            linewidth=0.8,
            label=response_labels[i],
        )

        for j, width in enumerate(widths):

            if width >= 8:
                ax.text(
                    left[j] + width / 2,
                    y[j],
                    f"{width:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="black" if i < 3 else "white",
                )

        left += widths

    # Y-axis
    ax.set_yticks(y)
    ax.set_yticklabels(
        [distribution[0] for distribution in distributions],
        fontsize=9,
    )

    # X-axis
    ax.set_xlim(0, 100)
    ax.set_xlabel(
        "Participants (%)",
        fontsize=9,
    )

    ax.set_xticks(np.arange(0, 101, 20))
    ax.tick_params(
        axis="x",
        labelsize=8,
    )

    ax.tick_params(
        axis="y",
        length=0,
    )

    ax.invert_yaxis()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.grid(
        axis="x",
        linestyle="--",
        linewidth=0.5,
        alpha=0.3,
    )

    ax.set_axisbelow(True)

    ax.legend(
        title="Likert response",
        ncol=5,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.25),
        frameon=False,
        fontsize=8,
        title_fontsize=8,
        handlelength=1.2,
        columnspacing=1.2,
    )

    plt.tight_layout()

    fig.savefig(
        "results/survey_analysis/plots/explicit_intent_likert.pdf",
        format="pdf",
        bbox_inches="tight",
    )

    return fig, ax
def plot_explicit_intent_likertold(df):
    """
    Plot Likert-response distributions for the main explicit-intent
    perception questions from Scenario 4.

    Saves:
        results/survey_analysis/plots/explicit_intent_likert.pdf
    """
    import matplotlib.pyplot as plt
    import numpy as np

    questions = {
        "Projection clarity": "PostS4_Q1_ProjClarity",
        "Earlier path alteration": "PostS4_Q3_EarlyPathAlter",
        "Reduced anxiety": "PostS4_Q4_ReducedAnxiety",
    }

    likert_values = [1, 2, 3, 4, 5]

    distributions = []

    for label, col in questions.items():
        values = df[col].dropna()

        counts = values.value_counts().reindex(likert_values, fill_value=0)
        percentages = counts / counts.sum() * 100

        distributions.append((label, percentages.values))

    fig, ax = plt.subplots(figsize=(7, 2.8))

    left = np.zeros(len(distributions))

    for i, value in enumerate(likert_values):
        widths = np.array([dist[1][i] for dist in distributions])

        ax.barh(
            range(len(distributions)),
            widths,
            left=left,
            height=0.65,
            label=str(value),
        )

        left += widths

    ax.set_yticks(range(len(distributions)))
    ax.set_yticklabels([dist[0] for dist in distributions])

    ax.set_xlim(0, 100)
    ax.set_xlabel("Participants (%)")
    ax.set_xlabel("Participants (%)")

    ax.set_xticks(np.arange(0, 101, 20))
    ax.legend(
        title="Likert response",
        ncol=5,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.25),
        frameon=False,
    )

    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)

    plt.tight_layout()

    fig.savefig(
        "results/survey_analysis/plots/explicit_intent_likert.pdf",
        format="pdf",
        bbox_inches="tight",
    )

    return fig, ax