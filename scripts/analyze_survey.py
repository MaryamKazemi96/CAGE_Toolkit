
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from src.survey.data import load_survey, RELATED_ITEM_GROUPS, PREFERENCE_LABELS
from src.survey.stats import (
    run_related_group_tests,
    tlx_density_test,
    preference_analysis,
    spearman_correlation,
)
from src.survey.plots import plot_explicit_intent_likert,plot_preference_transition, plot_related_group_bars, plot_tlx_density_kde, plot_preference_bar

# ---------------------------------------------------------------------

INPUT_CSV = Path("data/survey/survey.csv")

OUTPUT = Path("results/survey_analysis")
PLOTS = OUTPUT / "plots"
OUTPUT.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)


def format_one_sample(label: str, res: dict) -> list[str]:

    lines = [f"  {label}: n={res['n']}"]

    if res["n"] < 2:
        lines.append(f"    {res.get('note', 'Insufficient data.')}")
        return lines

    lines.append(f"    Mean={res['mean']:.2f}  Median={res['median']:.1f}")
    if "t_p" in res:
        lines.append(f"    One-sample t-test vs. neutral(3): t={res['t_stat']:.2f}, p={res['t_p']:.4f}")
    if "wilcoxon_p" in res:
        lines.append(f"    Wilcoxon signed-rank vs. neutral(3): W={res['wilcoxon_stat']:.2f}, p={res['wilcoxon_p']:.4f}")

    return lines


def main() -> None:

    df = load_survey(INPUT_CSV, verbose=True)
    plot_explicit_intent_likert(df)

    print(f"\nLoaded {len(df)} participants across {df['session'].nunique()} sessions.")
    print(f"Density breakdown: {df['density'].value_counts().to_dict()}")

    df.to_csv(OUTPUT / "cleaned_survey.csv", index=False)

    report: list[str] = [f"Cage survey analysis -- {len(df)} participants, {df['session'].nunique()} sessions\n"]

   
    report.append("=" * 78)
    report.append("IMPLICIT (S3) vs EXPLICIT (S4) related items -- INDEPENDENT one-sample")
    report.append("tests only (different wording per condition; no paired test run)")
    report.append("=" * 78)

    group_results = run_related_group_tests(df)

    for gres in group_results:

        meta = gres["group_meta"]

        report.append(f"\n--- {meta['construct']} ---")
        report.append(f"  Implicit (S3) question: \"{meta['implicit']['question']}\"")
        report.append(f"  Explicit (S4) question: \"{meta['explicit']['question']}\"")
        report.extend(format_one_sample(f"Implicit [{meta['implicit']['col']}]", gres["implicit"]))
        report.extend(format_one_sample(f"Explicit [{meta['explicit']['col']}]", gres["explicit"]))

        fig, ax = plot_related_group_bars(gres)
        fig.tight_layout()
        slug = meta["construct"].lower().replace(" ", "_").replace("/", "-")
        fig.savefig(PLOTS / f"related_{slug}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    
    report.append("\n" + "=" * 78)
    report.append("NASA-TLX WORKLOAD by crowd density (low vs high)")
    report.append("=" * 78)

    tlx_res = tlx_density_test(df)

    report.append(
        f"Low density:  n={tlx_res['n_low']}, mean={tlx_res['mean_low']:.2f}, "
        f"median={tlx_res['median_low']:.2f}"
    )
    report.append(
        f"High density: n={tlx_res['n_high']}, mean={tlx_res['mean_high']:.2f}, "
        f"median={tlx_res['median_high']:.2f}"
    )
    if "mannwhitney_p" in tlx_res:
        report.append(f"Mann-Whitney U: U={tlx_res['mannwhitney_u']:.2f}, p={tlx_res['mannwhitney_p']:.4f}")
        report.append(f"Welch's t-test: t={tlx_res['welch_t']:.2f}, p={tlx_res['welch_p']:.4f}")

    fig, ax = plot_tlx_density_kde(df)
    fig.tight_layout()
    fig.savefig(PLOTS / "tlx_density_kde.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

   
    report.append("\n" + "=" * 78)
    report.append("ROBOT PREFERENCE: SCENARIO 3 vs SCENARIO 4")
    report.append("=" * 78)

    S3_PREF = "PostS3_Q5_S3Preference"
    S4_PREF = "PostS4_Q5_FinalPreference"

    pref_res = preference_analysis(
        df,
        col_s3=S3_PREF,
        col_s4=S4_PREF,
    )

    report.append(
        f"\nPaired observations: n={pref_res['n_pairs']}"
    )

    report.append("\nScenario 3 (implicit) preference:")
    for category, label in PREFERENCE_LABELS.items():
        n = pref_res["s3_counts"].loc[category]
        report.append(f"  {label:20s} {n}")

    report.append("\nScenario 4 (explicit) preference:")
    for category, label in PREFERENCE_LABELS.items():
        n = pref_res["s4_counts"].loc[category]
        report.append(f"  {label:20s} {n}")

    report.append("\nTransition matrix (rows = S3, columns = S4):")
    report.append(
        pref_res["transition"]
        .rename(index=PREFERENCE_LABELS, columns=PREFERENCE_LABELS)
        .to_string()
    )

    if "bowker_p" in pref_res:
        report.append(
            f"\nBowker's test of symmetry: "
            f"chi2={pref_res['bowker_chi2']:.2f}, "
            f"df={pref_res['bowker_df']}, "
            f"p={pref_res['bowker_p']:.4f}"
        )

    report.append("\nNet category changes (S4 - S3):")
    for category, label in PREFERENCE_LABELS.items():
        change = pref_res["net_change"].loc[category]
        report.append(f"  {label:20s} {change:+d}")

    fig, ax = plot_preference_transition(pref_res)
    fig.tight_layout()
    fig.savefig(
        PLOTS / "preference_s3_vs_s4.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)
 
  
    report.append("\n" + "=" * 78)
    report.append("EXPLORATORY: individual differences vs. outcomes (Spearman)")
    report.append("=" * 78)

    corr_pairs = [
        ("PRS_recomputed", "PostS3_Q3_Hesitation", "Risk propensity vs. implicit-condition hesitation"),
        ("PRS_recomputed", "PostS3_Q4_ForcedToYield", "Risk propensity vs. implicit-condition forced-yield"),
        ("Pre_Q2_Trust", "PostS3_Q2_DelivLegibility", "Prior trust in robots vs. implicit legibility rating"),
        ("Pre_Q2_Trust", "PostS4_Q1_ProjClarity", "Prior trust in robots vs. explicit (projection) clarity rating"),
    ]

    for col_a, col_b, label in corr_pairs:

        res = spearman_correlation(df, col_a, col_b)

        if "rho" in res:
            report.append(f"\n{label}: n={res['n']}, Spearman rho={res['rho']:.3f}, p={res['p']:.4f}")
        else:
            report.append(f"\n{label}: insufficient data (n={res['n']}).")

    
    report_text = "\n".join(report)
    (OUTPUT / "stats_report.txt").write_text(report_text, encoding="utf-8")

    print("\n" + report_text)

    print(f"\n\nSaved cleaned data: {(OUTPUT / 'cleaned_survey.csv').resolve()}")
    print(f"Saved report:       {(OUTPUT / 'stats_report.txt').resolve()}")
    print(f"Saved plots:        {PLOTS.resolve()}")


if __name__ == "__main__":
    main()