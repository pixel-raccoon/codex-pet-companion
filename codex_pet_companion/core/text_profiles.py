from __future__ import annotations

DEFAULT_TEXT_PROFILE = "neutral"

TEXT_PROFILE_BY_PET_ID: dict[str, str] = {
    "lumisprout": "lumisprout",
    "vikamon": "vikamon",
}

def text_profile_id(pet_id: str) -> str:
    return TEXT_PROFILE_BY_PET_ID.get(str(pet_id or "").strip().lower(), DEFAULT_TEXT_PROFILE)

def register_text_profile(pet_id: str, profile_id: str) -> None:
    pet_id = str(pet_id or "").strip().lower()
    profile_id = str(profile_id or "").strip().lower()
    if pet_id and profile_id:
        TEXT_PROFILE_BY_PET_ID[pet_id] = profile_id
