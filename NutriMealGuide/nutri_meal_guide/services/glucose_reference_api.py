from __future__ import annotations

from typing import Optional

import pandas as pd
import requests


def fetch_glucose_reference_from_api(url: str) -> Optional[pd.DataFrame]:
    """
    Try to fetch a glucose reference table from an external API.

    Expected JSON shape (example):
    [
      {
        "group": "Adults",
        "sex": "Women",
        "fasting_range_mg_dl": "70-99",
        "category": "Normal",
        "risk_score": 1
      }
    ]
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        raw = response.json()
    except Exception:
        return None

    if not isinstance(raw, list):
        return None

    records = []
    for row in raw:
        try:
            records.append(
                {
                    "Group": row.get("group", "Unknown"),
                    "Sex": row.get("sex", "All"),
                    "Fasting range (mg/dL)": row.get("fasting_range_mg_dl", ""),
                    "Category": row.get("category", ""),
                    "Risk score (1=low, 4=high)": int(row.get("risk_score", 0)),
                }
            )
        except Exception:
            continue

    if not records:
        return None

    return pd.DataFrame(records)

