from __future__ import annotations

import streamlit as st

from nutri_meal_guide.ui.pages.glucose_reference import render_glucose_reference
from nutri_meal_guide.ui.pages.gp_finder import render_gp_finder
from nutri_meal_guide.ui.pages.meal_planner import render_meal_planner


def main() -> None:
    st.set_page_config(
        page_title="Nutri Meal Guide",
        page_icon="🥗",
        layout="centered",
    )

    page = st.sidebar.radio(
        "Pages",
        ["Meal planner", "Blood sugar levels & risk", "Find a GP"],
        index=0,
    )

    if page == "Meal planner":
        st.title("Nutri Meal Guide")
        st.caption(
            "Personalized, diabetic-friendly meal suggestions based on your BMI and blood sugar."
        )
        render_meal_planner()
    elif page == "Blood sugar levels & risk":
        render_glucose_reference()
    else:
        render_gp_finder()

