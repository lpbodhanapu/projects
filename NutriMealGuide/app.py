import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st


BMI_THRESHOLDS = {
    "underweight": 18.5,
    "normal": 24.9,
    "overweight": 29.9,
}


def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    height_m = height_cm / 100.0
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    bmi = weight_kg / (height_m**2)
    bmi_rounded = round(bmi, 1)

    if bmi_rounded < BMI_THRESHOLDS["underweight"]:
        category = "Underweight"
    elif bmi_rounded <= BMI_THRESHOLDS["normal"]:
        category = "Normal weight"
    elif bmi_rounded <= BMI_THRESHOLDS["overweight"]:
        category = "Overweight"
    else:
        category = "Obese"

    return bmi_rounded, category


def classify_glucose(glucose_mg_dl: float) -> str:
    if glucose_mg_dl < 70:
        return "Low (Hypoglycemia risk)"
    if glucose_mg_dl < 100:
        return "Normal (fasting)"
    if glucose_mg_dl < 126:
        return "Pre-diabetic range"
    return "Diabetic range"


def get_meal_suggestions(
    diet_type: str, glucose_mg_dl: float
) -> Dict[str, List[str]]:
    glucose_class = classify_glucose(glucose_mg_dl)

    base_meals = {
        "Vegan": {
            "breakfast": [
                "Overnight oats with chia seeds, cinnamon, and berries (unsweetened plant milk)",
                "Tofu scramble with spinach, tomatoes, and mushrooms, plus a small slice of whole-grain toast",
            ],
            "lunch": [
                "Quinoa salad with chickpeas, cucumber, tomato, olive oil, and lemon",
                "Lentil and vegetable soup with a side of leafy green salad",
            ],
            "dinner": [
                "Stir-fried tofu with non-starchy vegetables (broccoli, bell peppers, snap peas) over cauliflower rice",
                "Baked eggplant with tomato sauce, served with steamed greens",
            ],
        },
        "Vegetarian": {
            "breakfast": [
                "Plain Greek yogurt with nuts, seeds, and a few berries",
                "Vegetable omelette (spinach, peppers, onions) with one slice whole-grain toast",
            ],
            "lunch": [
                "Mixed bean salad with avocado and leafy greens",
                "Paneer and vegetable stir-fry with a small portion of brown rice",
            ],
            "dinner": [
                "Vegetable curry (no cream) with a small portion of brown rice or whole-wheat roti",
                "Grilled paneer with roasted non-starchy vegetables",
            ],
        },
        "Non-vegetarian": {
            "breakfast": [
                "Scrambled eggs with spinach and mushrooms, plus a small slice of whole-grain toast",
                "Plain Greek yogurt with nuts and a few berries",
            ],
            "lunch": [
                "Grilled chicken salad with olive oil dressing (no croutons)",
                "Baked fish with steamed vegetables and a small portion of quinoa",
            ],
            "dinner": [
                "Grilled chicken or fish with roasted non-starchy vegetables",
                "Turkey or chicken lettuce wraps with crunchy vegetables",
            ],
        },
    }

    adjustments = {
        "Low (Hypoglycemia risk)": [
            "Include a small portion of low-glycemic carbs (e.g., half a banana, whole-grain toast) along with a protein source.",
            "Monitor symptoms and follow your clinician's advice for treating low sugar.",
        ],
        "Normal (fasting)": [
            "Maintain balanced meals with lean protein, healthy fats, and high-fiber carbs.",
            "Avoid sugary drinks and refined sweets.",
        ],
        "Pre-diabetic range": [
            "Focus on high-fiber, low-glycemic carbs (lentils, beans, non-starchy vegetables).",
            "Keep portions of whole grains small and pair with protein.",
        ],
        "Diabetic range": [
            "Prioritize non-starchy vegetables and lean protein; keep starchy carbs very limited.",
            "Avoid fruit juices and sweetened foods; prefer whole fruits in moderation.",
        ],
    }

    meals = base_meals.get(diet_type, base_meals["Non-vegetarian"])
    return {
        "glucose_class": glucose_class,
        "breakfast": meals["breakfast"],
        "lunch": meals["lunch"],
        "dinner": meals["dinner"],
        "guidance": adjustments[glucose_class],
    }


def _map_diet_to_api_param(diet_type: str) -> str:
    mapping = {
        "Vegan": "vegan",
        "Vegetarian": "vegetarian",
        "Non-vegetarian": "",
    }
    return mapping.get(diet_type, "")


def fetch_diabetic_friendly_meals(
    diet_type: str,
    glucose_mg_dl: float,
    api_key: str,
    per_meal: int = 4,
) -> Dict[str, List[Dict[str, str]]]:
    """
    Fetch diabetic-friendly meal ideas from the Spoonacular API.

    Returns a dict:
        {
          "Breakfast": [{"title": ..., "image": ...}, ...],
          "Lunch": [...],
          "Dinner": [...],
        }
    Falls back to empty lists on any error; caller should handle fallback.
    """
    if not api_key:
        return {"Breakfast": [], "Lunch": [], "Dinner": []}

    base_url = "https://api.spoonacular.com/recipes/complexSearch"
    diet_param = _map_diet_to_api_param(diet_type)

    # Stricter sugar limits for higher glucose.
    if glucose_mg_dl < 100:
        max_sugar = 20
    elif glucose_mg_dl < 126:
        max_sugar = 15
    else:
        max_sugar = 10

    meal_type_map = {
        "Breakfast": "breakfast",
        "Lunch": "main course",
        "Dinner": "main course",
    }

    results: Dict[str, List[Dict[str, str]]] = {
        "Breakfast": [],
        "Lunch": [],
        "Dinner": [],
    }

    for label, meal_type in meal_type_map.items():
        params = {
            "apiKey": api_key,
            "number": per_meal,
            "type": meal_type,
            "diet": diet_param,
            "addRecipeNutrition": "true",
            "maxSugar": max_sugar,
            "sort": "healthiness",
        }
        try:
            resp = requests.get(base_url, params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            continue

        items = []
        for r in data.get("results", []):
            title = r.get("title")
            image = r.get("image")
            if not title:
                continue
            items.append(
                {
                    "title": title,
                    "image": image or "",
                }
            )

        results[label] = items

    return results


def fetch_glucose_reference_from_api(
    url: str,
) -> Optional[pd.DataFrame]:
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
      },
      ...
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

        suggestions = get_meal_suggestions(diet_type, glucose_mg_dl)

        key_file = Path("spoonacular_key.txt")
        api_key = ""
        if key_file.exists():
            api_key = key_file.read_text(encoding="utf-8").strip()

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

    profile = st.session_state["profile"]
    if profile is None:
        st.info("Fill in your details and click **Get my meal plan**.")
        return

    height_cm = profile["height_cm"]
    weight_kg = profile["weight_kg"]
    glucose_mg_dl = profile["glucose_mg_dl"]
    diet_type = profile["diet_type"]
    bmi = profile["bmi"]
    bmi_category = profile["bmi_category"]
    suggestions = profile["suggestions"]
    api_meals = st.session_state["api_meals"]

    # Show snapshot only on the first step; keep the menu page focused.
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

    # Step-like navigation controlled by session state
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

    # Page 1: show only cards with images and a select button
    if not st.session_state["show_meal_options"]:
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

    # Page 2: show options for the selected meal
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

    # Prefer live API meals if available; fall back to built-in suggestions.
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


def render_glucose_reference() -> None:
    st.title("Blood Sugar Levels & Risk")
    st.caption(
        "Reference ranges for blood glucose. Always confirm targets with your own clinician."
    )

    st.subheader("Typical fasting (before meal) ranges by group")

    # API endpoint can be configured here. Replace this with a real
    # open-source or internal API that returns JSON in the documented format.
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

    # Built-in fallback table consistent with common guidelines.
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


def main() -> None:
    st.set_page_config(
        page_title="Nutri Meal Guide",
        page_icon="🥗",
        layout="centered",
    )

    page = st.sidebar.radio(
        "Pages",
        ["Meal planner", "Blood sugar levels & risk"],
        index=0,
    )

    if page == "Meal planner":
        render_meal_planner()
    else:
        render_glucose_reference()


if __name__ == "__main__":
    main()