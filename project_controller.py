import os

from paths import (
    get_current_project_file,
    get_projects_dir
)


CURRENT_PROJECT_FILE = get_current_project_file()
PROJECTS_DIR = get_projects_dir()


def set_current_project(config_path):

    with open(
        CURRENT_PROJECT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(str(config_path))


def get_current_project():

    if not os.path.exists(
        CURRENT_PROJECT_FILE
    ):
        return None

    with open(
        CURRENT_PROJECT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        path = f.read().strip()

    if not path:
        return None

    return path


def list_projects():

    if not os.path.exists(PROJECTS_DIR):
        return []

    return sorted(
        os.listdir(PROJECTS_DIR)
    )


def clear_current_project():

    with open(
        CURRENT_PROJECT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("")