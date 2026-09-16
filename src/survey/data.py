from __future__ import annotations

from pathlib import Path

import pandas as pd


SESSION_DENSITY = {
    "s1": "low", "s2": "low", "s3": "low", "s4": "low",
    "s5": "high", "s6": "high", "s7": "high", "s8": "low",
}


RPS_REVERSE_ITEMS = [
    "Pre_RPS_Q3_SafetyFirst",
    "Pre_RPS_Q4_AvoidRisks",
    "Pre_RPS_Q5_NoUnnecessaryRisks",
    "Pre_RPS_Q7_DislikeUnpredictable",
]
RPS_ASIS_ITEMS = [
    "Pre_RPS_Q6_TakeRisksRegularly",
    "Pre_RPS_Q8_CrowdsAsChallenge",
    "Pre_RPS_Q9_AssertiveNavigator",
]

TLX_ITEMS = [
    "TLX_Mental", "TLX_Physical", "TLX_Temporal",
    "TLX_Performance", "TLX_Effort", "TLX_Frustration",
]


RELATED_ITEM_GROUPS = [
    {
        "construct": "Robot Intent Legibility",
        "implicit": {
            "col": "PostS3_Q2_DelivLegibility",
            "label": "Implicit (S3)",
            "question": (
                "It was easy to understand where the delivery robot "
                "intended to go simply by looking at its physical movement."
            ),
        },
        "explicit": {
            "col": "PostS4_Q1_ProjClarity",
            "label": "Explicit (S4)",
            "question": (
                "The robot's destination displayed on the ground was "
                "clear and easy to read from a distance."
            ),
        },
    },
    {
        "construct": "Path Adaptation / Hesitation",
        "implicit": {
            "col": "PostS3_Q3_Hesitation",
            "label": "Implicit (S3)",
            "question": (
                "I found myself hesitating (stepping back and forth, or "
                "pausing) because I couldn't predict the robot's trajectory."
            ),
        },
        "explicit": {
            "col": "PostS4_Q3_EarlyPathAlter",
            "label": "Explicit (S4)",
            "question": (
                "Seeing the robot's destination projected on the floor "
                "allowed me to alter my path much earlier than in "
                "previous sessions."
            ),
        },
    },
    {
        "construct": "Perceived Safety",
        "implicit": {
            "col": "PostS3_Q4_ForcedToYield",
            "label": "Implicit (S3)",
            "question": (
                "In tight encounters, I felt forced to change my walking "
                "path because the robot wouldn't change its path."
            ),
        },
        "explicit": {
            "col": "PostS4_Q4_ReducedAnxiety",
            "label": "Explicit (S4)",
            "question": (
                "Knowing the robot's destination made me feel safer and "
                "less anxious sharing the bottleneck with it."
            ),
        },
    },
]

PREFERENCE_LABELS = {
    1: "Base robot",
    2: "Delivery robot",
    3: "Equally easy",
    4: "Equally difficult",
}



def load_clean(path: Path) -> pd.DataFrame:
    """Load survey.csv, drop stray trailing columns, coerce to numeric."""

    df = pd.read_csv(path)

    df = df[[c for c in df.columns if not c.startswith("Unnamed")]]


    text_columns = {"Session_ID", "PostS4_Comments"}
    for col in df.columns:
        if col not in text_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["session"] = df["Session_ID"].str.replace("s", "", regex=False).astype(int)
    df["density"] = df["Session_ID"].map(SESSION_DENSITY)

    return df


def add_derived_scores(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Reconstruct PRS (Risk Propensity Scale) and TLX (NASA-TLX) from raw
    items. Cross-checks the reconstruction against the sheet's own
    PRS/TLX columns if present.
    """

    df = df.copy()

    reversed_rps = df[RPS_REVERSE_ITEMS].apply(lambda col: 10 - col)
    asis_rps = df[RPS_ASIS_ITEMS]

    df["PRS_recomputed"] = pd.concat([reversed_rps, asis_rps], axis=1).mean(axis=1)
    df["TLX_recomputed"] = df[TLX_ITEMS].mean(axis=1)

    if verbose:
        if "PRS" in df.columns:
            bad = (df["PRS_recomputed"] - df["PRS"]).abs() > 1e-6
            if bad.any():
                print(f"WARNING: PRS_recomputed differs from sheet's PRS column for {bad.sum()} row(s).")
            else:
                print("OK: PRS_recomputed matches the sheet's PRS column for all rows.")

        if "TLX" in df.columns:
            bad = (df["TLX_recomputed"] - df["TLX"]).abs() > 1e-6
            if bad.any():
                print(f"WARNING: TLX_recomputed differs from sheet's TLX column for {bad.sum()} row(s).")
            else:
                print("OK: TLX_recomputed matches the sheet's TLX column for all rows.")

    return df


def load_survey(path: Path, verbose: bool = True) -> pd.DataFrame:
    """Convenience wrapper: load_clean() + add_derived_scores()."""

    df = load_clean(path)
    df = add_derived_scores(df, verbose=verbose)
    return df