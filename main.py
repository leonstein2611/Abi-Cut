# =========================
# main.py
# =========================

from startscreen import StartScreen
from project_wizard import ProjectWizard
from project_manager import ProjectManager
from gui import MusicGUI
from live_controller import LiveController


state = "menu"
config_path = None

while True:

    # ---------------------------------
    # StartScreen
    # ---------------------------------

    if state == "menu":

        
        
        window = StartScreen()

        result = window.show()

        if result is None:
            break

        if isinstance(result, tuple):

            state = result[0]

            if len(result) > 1:
                config_path = result[1]

        else:

            state = result

        continue

    # ---------------------------------
    # Projekt Wizard
    # ---------------------------------

    elif state == "wizard":

        window = ProjectWizard()
        result = window.show()

        if result is None:

            state = "menu"
            continue

        if isinstance(result, tuple):

            state = result[0]

            if len(result) > 1:
                config_path = result[1]

        else:

            state = result

        continue

    # ---------------------------------
    # Projektmanager
    # ---------------------------------

    elif state == "manager":

        window = ProjectManager()
        result = window.show()

        if result is None:

            state = "menu"
            continue

        if isinstance(result, tuple):

            state = result[0]

            if len(result) > 1:
                config_path = result[1]

        else:

            state = result

        continue

    # ---------------------------------
    # Editor
    # ---------------------------------

    elif state == "editor":

        window = MusicGUI(config_path)
        result = window.show()

        if result is None:

            state = "menu"
            continue

        state = result
        continue

    # ---------------------------------
    # Live
    # ---------------------------------

    elif state == "live":

        window = LiveController(config_path)
        result = window.show()

        if result is None:

            state = "menu"
            continue

        state = result
        continue

    # ---------------------------------
    # Beenden
    # ---------------------------------

    elif state == "exit":

        break

    else:

        print("Unbekannter Zustand:", state)
        break