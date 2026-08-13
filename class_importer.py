import json
import uuid
from datetime import datetime

import pandas as pd

import tkinter as tk
from tkinter import messagebox

from settings_manager import get_defaults

defaults = get_defaults()

import os

def create_project_from_classlist(
    excel_file,
    project_name="Neues AbiCut Projekt"
):
    #Ein Projektordner erstellen

    duplicate_count = 0
    empty_rows_count = 0

    project_folder = os.path.join(
    "projects",
    project_name
    )

    os.makedirs(project_folder, exist_ok=True)
    os.makedirs(os.path.join(project_folder, "backups"), exist_ok=True)
    os.makedirs(os.path.join(project_folder, "exports"), exist_ok=True)
    os.makedirs(os.path.join(project_folder, "media"), exist_ok=True)

    output_file = os.path.join(
        project_folder,
        "config.json"
    )

    # Excel laden
    df = pd.read_excel(excel_file)

    def find_column(columns, aliases):

        for alias in aliases:

            if alias in columns:
                return columns.index(alias)

        return None

    slides = {}

    slide_number = 2 # start mit 2, da Slide 1 der Intro-Slide ist
    
    # Spaltennamen vereinheitlichen
    columns = [
        str(c).lower().strip()
        for c in df.columns
    ]

        # -----------------------------
        # Name automatisch erkennen
        # -----------------------------

    name_index = find_column(
            columns,
            [
                "voller name",
                "full name",
                "schülername",
                "schuelername"
            ]
        )

    first_index = find_column(
            columns,
            [
                "vorname",
                "name",
                "first name",
                "firstname",
                "rufname"
            ]
        )

    last_index = find_column(
            columns,
            [
                "nachname",
                "familienname",
                "surname",
                "last name",
                "lastname"
            ]
        )    
    

    used_names = set()
    

    for _, row in df.iterrows():


        if first_index is not None and last_index is not None:

            first = str(row.iloc[first_index]).replace("nan", "").strip()
            last = str(row.iloc[last_index]).replace("nan", "").strip()

            student = f"{first} {last}"
            student = " ".join(student.split()).strip()

            if student == "":
                empty_rows_count += 1
                continue

            if student == "" or student.lower() == "nan":
                empty_rows_count += 1
                continue

            if student in used_names:

                messagebox.showwarning(
                    "Doppelter Name",
                    f"{student} kommt mehrfach vor."
                )

                duplicate_count += 1

            used_names.add(student)
            

        elif name_index is not None:

            student = str(row.iloc[name_index]).strip()

            student = " ".join(student.split())
            student = student.strip()

            if student == "" or student.lower() == "nan":
                empty_rows_count += 1
                continue

            if student in used_names:

                messagebox.showwarning(
                    "Doppelter Name",
                    f"{student} kommt mehrfach vor."
                )

                duplicate_count += 1

            used_names.add(student)

        else:

            raise Exception(
                "Keine geeigneten Namensspalten gefunden."
            )
        

        slides[str(slide_number)] = {

            "student": student,

            "student_id": str(uuid.uuid4()),

            "song": "",

            "artist": "",

            "uri": "",

            #Standardwerte für die Folien

            "start_ms": 0,

            "duration_ms": defaults["song_duration"], #30 Sekunden Standarddauer

            "fade_in": defaults["fade_in"],

            "fade_out": defaults["fade_out"],

            "enabled": True,

            "song_added": False,

            "time_confirmed": False
        }

        slide_number += 1

    config = {

        "project": {

            "name": project_name,

            "school": "",

            "graduation_year": "",

            "created": datetime.now().strftime(
                "%d.%m.%Y"
            ),

            "last_opened": "",

            "version": "1.0.0"

        },

        "slides": slides

    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            config,
            f,
            indent=4,
            ensure_ascii=False
        )

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        recognized = []

        if first_index is not None:
            recognized.append(f"✓ Vorname erkannt")
            recognized.append(f"    → {df.columns[first_index]}")

        if last_index is not None:
            recognized.append(f"✓ Nachname erkannt")
            recognized.append(f"    → {df.columns[last_index]}")

        if name_index is not None:
            recognized.append(f"✓ Vollständiger Name erkannt")
            recognized.append(f"    → {df.columns[name_index]}")

        recognition_text = "\n        ".join(recognized)

        messagebox.showinfo(

            "AbiCut",

            f"""
        ────────────────────────

        Projekt erfolgreich erstellt

        ────────────────────────

        Projekt:
        {project_name}

        Schüler importiert:
        {len(slides)}

        Folien:
        2 bis {slide_number-1}

        Projektdatei:
        {output_file}

        ────────────────────────

        Erkannte Spalten

        {recognition_text}

        ────────────────────────

        Import-Statistik

        ✓ Schüler importiert: {len(slides)}
        ⚠ Doppelte Namen: {duplicate_count}
        ⚠ Leere Zeilen übersprungen: {empty_rows_count}

        ────────────────────────

        ✓ Das Projekt ist jetzt bereit.

        Als Nächstes kann eine Spotify-
        Playlist importiert oder direkt
        mit dem Bearbeiten begonnen werden.

        ────────────────────────
        """
        )
        root.destroy()

    print(
            f"Projekt erstellt ({len(slides)} Schüler)"
        )
    
    return output_file

if __name__ == "__main__":

    excel_file = input(
        "Klassenliste (.xlsx): "
    )

    project_name = input(
        "Projektname: "
    )

    create_project_from_classlist(
        excel_file,
        project_name=project_name
    )

