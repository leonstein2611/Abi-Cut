import os
import json

CURRENT_PROJECT_FILE = "current_project.txt"


def set_current_project(config_path):

    with open(CURRENT_PROJECT_FILE, "w") as f:
        f.write(config_path)


def get_current_project():

    if not os.path.exists(CURRENT_PROJECT_FILE):
        return None

    with open(CURRENT_PROJECT_FILE) as f:
        return f.read().strip()


def list_projects():

    if not os.path.exists("projects"):
        return []

    return sorted(os.listdir("projects"))

def clear_current_project():

    with open("current_project.txt", "w") as f:
        f.write("")