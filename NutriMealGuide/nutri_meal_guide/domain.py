from __future__ import annotations

from typing import Dict, List, Tuple


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


def built_in_meal_suggestions(
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

