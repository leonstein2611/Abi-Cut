import json


# =========================
# Config laden
# =========================

def load_project_statistics(config_path):

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as f:

        config = json.load(f)

    return calculate_statistics(config)


# =========================
# Statistik berechnen
# =========================

def calculate_statistics(config):

    slides = config["slides"]

    total = len(slides)

    enabled = 0
    disabled = 0

    songs = 0
    confirmed = 0

    for slide in slides.values():

        if slide.get("enabled", True):
            enabled += 1
        else:
            disabled += 1

        if slide.get("song_added", False):
            songs += 1

        if slide.get("time_confirmed", False):
            confirmed += 1

    progress = 0

    if total > 0:
        progress = round(
            confirmed / total * 100
        )

    return {

        "project_name":
            config["project"].get("name", ""),

        "school":
            config["project"].get("school", ""),

        "graduation_year":
            config["project"].get("graduation_year", ""),

        "created":
            config["project"].get("created", ""),

        "last_opened":
            config["project"].get("last_opened", ""),

        "version":
            config["project"].get("version", ""),

        "total":
            total,

        "enabled":
            enabled,

        "disabled":
            disabled,

        "songs":
            songs,

        "confirmed":
            confirmed,

        "progress":
            progress
    }


# =========================
# Fortschrittsbalken
# =========================

def create_progress_bar(progress):

    filled = int(progress / 5)

    return (
        "█" * filled +
        "░" * (20 - filled)
    )