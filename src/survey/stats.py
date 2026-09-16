
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.survey.data import PREFERENCE_LABELS


def one_sample_test(df: pd.DataFrame, col: str, reference: float = 3.0) -> dict:


    values = df[col].dropna().to_numpy(float)
    n = len(values)

    result = {
        "col": col,
        "reference": reference,
        "n": n,
        "mean": float(np.mean(values)) if n else None,
        "median": float(np.median(values)) if n else None,
        "values": values,
    }

    if n < 2:
        result["note"] = "Not enough data for a test."
        return result

    tstat, tp = stats.ttest_1samp(values, reference)
    result["t_stat"] = float(tstat)
    result["t_p"] = float(tp)

    sem = stats.sem(values)
    ci = sem * stats.t.ppf(0.975, n - 1)
    result["ci_low"] = result["mean"] - ci
    result["ci_high"] = result["mean"] + ci

    diff = values - reference
    if np.any(diff != 0):
        try:
            wstat, wp = stats.wilcoxon(diff)
            result["wilcoxon_stat"] = float(wstat)
            result["wilcoxon_p"] = float(wp)
        except ValueError as e:
            result["wilcoxon_error"] = str(e)

    return result


def paired_test(df: pd.DataFrame, col_a: str, col_b: str) -> dict:
   
    sub = df[[col_a, col_b]].dropna()

    a = sub[col_a].to_numpy(float)
    b = sub[col_b].to_numpy(float)

    n = len(a)

    result = {
        "col_a": col_a,
        "col_b": col_b,
        "n_pairs": n,
        "mean_a": float(np.mean(a)) if n else None,
        "mean_b": float(np.mean(b)) if n else None,
        "median_a": float(np.median(a)) if n else None,
        "median_b": float(np.median(b)) if n else None,
    }

    if n < 2:
        result["note"] = "Not enough complete pairs for a test."
        return result

    diff = a - b

    if np.all(diff == 0):
        result["note"] = "All differences are zero; no test performed."
        return result

    try:
        wstat, wp = stats.wilcoxon(a, b)
        result["wilcoxon_stat"] = float(wstat)
        result["wilcoxon_p"] = float(wp)
    except ValueError as e:
        result["wilcoxon_error"] = str(e)

    tstat, tp = stats.ttest_rel(a, b)
    result["paired_t_stat"] = float(tstat)
    result["paired_t_p"] = float(tp)

    d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0.0
    result["cohens_d"] = float(d)

    return result


def run_related_group_tests(df: pd.DataFrame, reference: float = 3.0) -> list[dict]:
   
    from src.survey.data import RELATED_ITEM_GROUPS

    results = []

    for group in RELATED_ITEM_GROUPS:

        implicit_res = one_sample_test(df, group["implicit"]["col"], reference=reference)
        explicit_res = one_sample_test(df, group["explicit"]["col"], reference=reference)

        results.append({
            "group_meta": group,
            "implicit": implicit_res,
            "explicit": explicit_res,
        })

    return results


def tlx_density_test(df: pd.DataFrame) -> dict:
    
    low = df.loc[df["density"] == "low", "TLX_recomputed"].dropna()
    high = df.loc[df["density"] == "high", "TLX_recomputed"].dropna()

    result = {
        "n_low": len(low),
        "n_high": len(high),
        "mean_low": float(low.mean()) if len(low) else None,
        "mean_high": float(high.mean()) if len(high) else None,
        "median_low": float(low.median()) if len(low) else None,
        "median_high": float(high.median()) if len(high) else None,
        "low_values": low,
        "high_values": high,
    }

    if len(low) >= 2 and len(high) >= 2:

        ustat, up = stats.mannwhitneyu(low, high, alternative="two-sided")
        result["mannwhitney_u"] = float(ustat)
        result["mannwhitney_p"] = float(up)

        tstat, tp = stats.ttest_ind(low, high, equal_var=False)
        result["welch_t"] = float(tstat)
        result["welch_p"] = float(tp)

    return result



def preference_analysis(
    df: pd.DataFrame,
    col_s3: str,
    col_s4: str,
) -> dict:
    """
    Compare paired categorical preferences between Scenario 3 (implicit)
    and Scenario 4 (explicit).

    Uses Bowker's test of symmetry for paired nominal data with four
    response categories.

    Categories:
        1 = Base robot
        2 = Delivery robot
        3 = Equally easy
        4 = Equally difficult
    """

    sub = df[[col_s3, col_s4]].dropna()

    s3 = sub[col_s3].astype(int)
    s4 = sub[col_s4].astype(int)

    categories = list(PREFERENCE_LABELS.keys())
    labels = list(PREFERENCE_LABELS.values())

    transition = pd.crosstab(s3, s4)

    transition = transition.reindex(
        index=categories,
        columns=categories,
        fill_value=0,
    )

    result = {
        "col_s3": col_s3,
        "col_s4": col_s4,
        "n_pairs": len(sub),
        "transition": transition,
        "labels": labels,
    }

    if len(sub) < 2:
        result["note"] = "Not enough paired observations."
        return result


    chi2 = 0.0
    df_test = 0
    valid_pairs = []

    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):

            nij = transition.iloc[i, j]
            nji = transition.iloc[j, i]

            if nij + nji > 0:
                chi2 += (nij - nji) ** 2 / (nij + nji)
                df_test += 1

                valid_pairs.append({
                    "from": labels[i],
                    "to": labels[j],
                    "nij": int(nij),
                    "nji": int(nji),
                })

    if df_test > 0:
        p = stats.chi2.sf(chi2, df_test)

        result["bowker_chi2"] = float(chi2)
        result["bowker_df"] = int(df_test)
        result["bowker_p"] = float(p)

    
    s3_counts = s3.value_counts().reindex(categories, fill_value=0)
    s4_counts = s4.value_counts().reindex(categories, fill_value=0)

    result["s3_counts"] = s3_counts
    result["s4_counts"] = s4_counts


    result["net_change"] = s4_counts - s3_counts

    return result

def spearman_correlation(df: pd.DataFrame, col_a: str, col_b: str) -> dict:
    """Spearman correlation between two columns, complete-case only."""

    sub = df[[col_a, col_b]].dropna()

    result = {"col_a": col_a, "col_b": col_b, "n": len(sub)}

    if len(sub) >= 3:
        rho, p = stats.spearmanr(sub[col_a], sub[col_b])
        result["rho"] = float(rho)
        result["p"] = float(p)

    return result