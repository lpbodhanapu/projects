from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from nutri_meal_guide.domain import built_in_meal_suggestions, calculate_bmi
from nutri_meal_guide.services.keys import read_spoonacular_key
from nutri_meal_guide.services.spoonacular import fetch_diabetic_friendly_meals


def render_meal_planner() -> None:
    if "profile" not in st.session_state:
        st.session_state["profile"] = None
    if "api_meals" not in st.session_state:
        st.session_state["api_meals"] = {"Breakfast": [], "Lunch": [], "Dinner": []}

    with st.form("user_input"):
        col1, col2 = st.columns(2)
        with col1:
            height_cm = st.number_input(
                "Height (cm)", min_value=80.0, max_value=250.0, value=170.0, step=1.0
            )
        with col2:
            weight_kg = st.number_input(
                "Weight (kg)", min_value=25.0, max_value=250.0, value=70.0, step=0.5
            )

        glucose_mg_dl = st.number_input(
            "Current blood sugar (mg/dL)",
            min_value=40.0,
            max_value=500.0,
            value=110.0,
            step=1.0,
            help="Use your latest fasting or pre-meal reading if possible.",
        )

        diet_type = st.selectbox(
            "Diet preference",
            options=["Vegan", "Vegetarian", "Non-vegetarian"],
            index=1,
        )

        submitted = st.form_submit_button("Get my meal plan")

    if submitted:
        try:
            bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
        except ValueError as exc:
            st.error(str(exc))
            return

        suggestions = built_in_meal_suggestions(diet_type, glucose_mg_dl)
        api_key = read_spoonacular_key()
        api_meals = fetch_diabetic_friendly_meals(diet_type, glucose_mg_dl, api_key)
        st.session_state["profile"] = {
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "glucose_mg_dl": glucose_mg_dl,
            "diet_type": diet_type,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "suggestions": suggestions,
        }
        st.session_state["api_meals"] = api_meals

    profile: Dict[str, Any] | None = st.session_state["profile"]
    if profile is None:
        st.info("Fill in your details and click **Get my meal plan**.")
        return

    glucose_mg_dl = float(profile["glucose_mg_dl"])
    diet_type = str(profile["diet_type"])
    bmi = profile["bmi"]
    bmi_category = profile["bmi_category"]
    suggestions = profile["suggestions"]
    api_meals = st.session_state["api_meals"]

    if "selected_meal" not in st.session_state:
        st.session_state["selected_meal"] = "Breakfast"
    if "show_meal_options" not in st.session_state:
        st.session_state["show_meal_options"] = False

    meal_cards = [
        {
            "name": "Breakfast",
            "image": "https://images.pexels.com/photos/4109413/pexels-photo-4109413.jpeg",
        },
        {
            "name": "Lunch",
            "image": "https://images.pexels.com/photos/1640773/pexels-photo-1640773.jpeg",
        },
        {
            "name": "Dinner",
            "image": "https://images.pexels.com/photos/262959/pexels-photo-262959.jpeg",
        },
    ]

    selected_meal = st.session_state["selected_meal"]

    if not st.session_state.get("show_meal_options", False):
        st.subheader("Your health snapshot")
        col_bmi, col_glucose = st.columns(2)
        with col_bmi:
            st.metric("BMI", f"{bmi}", bmi_category)
        with col_glucose:
            st.metric(
                "Blood sugar (mg/dL)",
                f"{glucose_mg_dl:.0f}",
                suggestions["glucose_class"],
            )

        if suggestions["glucose_class"].startswith("Low"):
            st.warning(
                "Your blood sugar appears low. If you feel unwell, follow your doctor's "
                "hypoglycemia plan and seek medical help if needed."
            )
        elif suggestions["glucose_class"].endswith("range"):
            st.warning(
                "Your blood sugar is above the normal fasting range. "
                "Discuss your readings and meal plan with your healthcare provider."
            )

        st.subheader("Personalized meal suggestions")
        st.markdown(f"**Diet preference:** {diet_type}")

        st.markdown("#### Choose a meal to customise")
        card_cols = st.columns(3)
        for col, card in zip(card_cols, meal_cards):
            with col:
                st.image(
                    card["image"],
                    caption=card["name"],
                    use_container_width=True,
                )
                if st.button(
                    f"Select {card['name']}",
                    key=f"select_{card['name'].lower()}",
                ):
                    st.session_state["selected_meal"] = card["name"]
                    st.session_state["show_meal_options"] = True
                    st.rerun()
        return

    # Menu page
    if selected_meal == "Breakfast":
        st.subheader(
            "Here are the recommended breakfast options based on your blood sugar and profile."
        )
    elif selected_meal == "Lunch":
        st.subheader(
            "Here are the recommended lunch options based on your blood sugar and profile."
        )
    else:
        st.subheader(
            "Here are the recommended dinner options based on your blood sugar and profile."
        )

    st.markdown(f"**Diet preference:** {diet_type}")

    if selected_meal in api_meals and api_meals[selected_meal]:
        meals_for_selected = api_meals[selected_meal]
        options = [m["title"] for m in meals_for_selected]
        images = [m.get("image") or "" for m in meals_for_selected]
    else:
        if selected_meal == "Breakfast":
            options = suggestions["breakfast"]
            images = [
                "https://images.pexels.com/photos/4109413/pexels-photo-4109413.jpeg"
            ] * len(options)
        elif selected_meal == "Lunch":
            options = suggestions["lunch"]
            images = [
                "https://images.pexels.com/photos/1640773/pexels-photo-1640773.jpeg"
            ] * len(options)
        else:
            options = suggestions["dinner"]
            images = [
                "https://images.pexels.com/photos/262959/pexels-photo-262959.jpeg"
            ] * len(options)

    if selected_meal == "Breakfast":
        label = "Pick your breakfast"
        meal_key = "breakfast"
    elif selected_meal == "Lunch":
        label = "Pick your lunch"
        meal_key = "lunch"
    else:
        label = "Pick your dinner"
        meal_key = "dinner"

    st.markdown("#### Options")
    for title, img_url in zip(options, images):
        col_img, col_text = st.columns([1, 2])
        with col_img:
            if img_url:
                st.image(img_url, use_container_width=True)
        with col_text:
            st.markdown(f"**{title}**")

    choice = st.radio(
        label,
        options=options,
        key=f"{meal_key}_choice",
    )

    st.markdown("### Your current selection")
    st.markdown(f"- **Meal:** {selected_meal}")
    st.markdown(f"- **Choice:** {choice}")

    if st.button("⬅ Back to meal selection", key="back_to_meal_cards"):
        st.session_state["show_meal_options"] = False
        st.rerun()

    st.subheader("General guidance")
    for tip in suggestions["guidance"]:
        st.markdown(f"- {tip}")

    st.caption(
        "This tool does **not** replace professional medical advice. "
        "Always follow the guidance of your healthcare team."
    )

