from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from nutri_meal_guide.services.glucose_reference_api import fetch_glucose_reference_from_api


def render_glucose_reference() -> None:
    st.title("Blood Sugar Levels & Risk")
    st.caption(
        "Reference ranges for blood glucose. Always confirm targets with your own clinician."
    )

    st.subheader("Typical fasting (before meal) ranges by group")

    api_url = st.text_input(
        "Optional: API URL for glucose reference data",
        value="",
        help=(
            "If you have an API that returns reference ranges as JSON, "
            "paste the URL here. Otherwise, the built-in table is used."
        ),
    )

    df_api: Optional[pd.DataFrame] = None
    if api_url:
        df_api = fetch_glucose_reference_from_api(api_url)
        if df_api is None:
            st.warning(
                "Could not load data from the API. Falling back to the built-in reference table."
            )

    data = [
        {
            "Group": "Children",
            "Sex": "All",
            "Fasting range (mg/dL)": "70–100",
            "Category": "Normal",
            "Risk score (1=low, 4=high)": 1,
        },
        {
            "Group": "Children",
            "Sex": "All",
            "Fasting range (mg/dL)": "< 70",
            "Category": "Low (hypoglycemia)",
            "Risk score (1=low, 4=high)": 4,
        },
        {
            "Group": "Adults",
            "Sex": "Women",
            "Fasting range (mg/dL)": "70–99",
            "Category": "Normal",
            "Risk score (1=low, 4=high)": 1,
        },
        {
            "Group": "Adults",
            "Sex": "Women",
            "Fasting range (mg/dL)": "100–125",
            "Category": "Pre-diabetic",
            "Risk score (1=low, 4=high)": 3,
        },
        {
            "Group": "Adults",
            "Sex": "Women",
            "Fasting range (mg/dL)": "≥ 126",
            "Category": "Diabetic range",
            "Risk score (1=low, 4=high)": 4,
        },
        {
            "Group": "Adults",
            "Sex": "Men",
            "Fasting range (mg/dL)": "70–99",
            "Category": "Normal",
            "Risk score (1=low, 4=high)": 1,
        },
        {
            "Group": "Adults",
            "Sex": "Men",
            "Fasting range (mg/dL)": "100–125",
            "Category": "Pre-diabetic",
            "Risk score (1=low, 4=high)": 3,
        },
        {
            "Group": "Adults",
            "Sex": "Men",
            "Fasting range (mg/dL)": "≥ 126",
            "Category": "Diabetic range",
            "Risk score (1=low, 4=high)": 4,
        },
        {
            "Group": "Older adults",
            "Sex": "All",
            "Fasting range (mg/dL)": "80–130",
            "Category": "Individualized target",
            "Risk score (1=low, 4=high)": 2,
        },
    ]

    df = df_api if df_api is not None else pd.DataFrame(data)
    styled = df.style.background_gradient(
        cmap="RdYlGn_r", subset=["Risk score (1=low, 4=high)"]
    )

    st.dataframe(styled, width="stretch")

    st.subheader("After-meal (1–2 hours post-meal) – general guidance")
    st.markdown(
        """
These ranges vary by country and guidelines. Common targets for many adults with diabetes are:

- Around **< 180 mg/dL** 1–2 hours after starting a meal.
- Your doctor may set a more strict or relaxed target depending on age, pregnancy, kidney function, etc.
        """
    )

    st.subheader("Safety notes")
    st.markdown(
        """
- If your sugar is **< 70 mg/dL** and you feel shaky, sweaty, or confused, follow your hypoglycemia treatment plan immediately.
- If your sugar is **consistently high** (for example, often above 180–200 mg/dL), talk to your healthcare provider about your medications and meal plan.
- Never change insulin or medication doses on your own without professional advice.
        """
    )

    st.caption(
        "This information is educational and may not match the exact targets recommended for you personally."
    )

