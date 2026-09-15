import sys
import shutil
from pathlib import Path

APP_NAME = "AbiCut"


def get_data_dir():
    """
    Benutzerordner für AbiCut-Daten.
    Beispiel:
    C:/Users/Leon/Documents/AbiCut
    """

    documents = Path.home() / "Documents"
    data_dir = documents / APP_NAME

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return data_dir


def get_projects_dir():

    projects_dir = get_data_dir() / "projects"

    projects_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return projects_dir


def get_settings_file():

    return get_data_dir() / "settings.json"


def get_current_project_file():

    return get_data_dir() / "current_project.txt"


def get_project_dir(project_name):

    return get_projects_dir() / project_name


def get_project_config(project_name):

    return get_project_dir(project_name) / "config.json"

def get_resource_dir():

    if getattr(sys, "frozen", False):

        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent

def get_app_icon():
    return get_resource_dir() / "assets" / "abicut_logo.ico"

def get_app_icon_png():
    return get_resource_dir() / "assets" / "abicut_logo.png"

def get_bundled_projects_dir():
    return get_resource_dir() / "bundled_projects"


def get_bundled_install_marker():
    return get_data_dir() / ".bundled_projects_installed"

def install_bundled_projects():

    marker = get_bundled_install_marker()

    # Übergabeprojekte wurden bereits einmal installiert
    if marker.exists():
        return

    source_dir = get_bundled_projects_dir()
    target_dir = get_projects_dir()

    if not source_dir.exists():
        return

    for project_folder in source_dir.iterdir():

        if not project_folder.is_dir():
            continue

        target_project = target_dir / project_folder.name

        if target_project.exists():
            continue

        shutil.copytree(
            project_folder,
            target_project
        )

    # Installation als abgeschlossen markieren
    marker.touch()

def get_spotify_cache_file():
    return get_data_dir() / ".spotify_cache"