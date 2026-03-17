from __future__ import annotations

from pathlib import Path

from nutri_meal_guide.config import SPOONACULAR_KEY_FILE


def read_spoonacular_key(path: Path = SPOONACULAR_KEY_FILE) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()

