from __future__ import annotations

from typing import Dict, List

import requests


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

    Returns:
        {
          "Breakfast": [{"title": ..., "image": ...}, ...],
          "Lunch": [...],
          "Dinner": [...],
        }
    """
    if not api_key:
        return {"Breakfast": [], "Lunch": [], "Dinner": []}

    base_url = "https://api.spoonacular.com/recipes/complexSearch"
    diet_param = _map_diet_to_api_param(diet_type)

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

    results: Dict[str, List[Dict[str, str]]] = {"Breakfast": [], "Lunch": [], "Dinner": []}

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

        items: List[Dict[str, str]] = []
        for r in data.get("results", []):
            title = r.get("title")
            image = r.get("image")
            if not title:
                continue
            items.append({"title": title, "image": image or ""})

        results[label] = items

    return results

