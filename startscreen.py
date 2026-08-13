# =========================
# startscreen.py
# =========================

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import subprocess

from baseWindow import BaseWindow

from project_controller import (
    get_current_project,
    set_current_project
)

from project_statistics import (
    load_project_statistics,
    create_progress_bar
)

from settings_window import SettingsWindow

from spotify_connection import SpotifyConnection

from project_wizard import ProjectWizard
from project_manager import ProjectManager

class StartScreen(BaseWindow):

    def __init__(self):

        super().__init__()

        

        self.root = tk.Tk()


        self.root.title("AbiCut")
        self.root.geometry("750x620")
        self.root.resizable(False, False)

        self.spotify = SpotifyConnection()

        self.spotify.connect()

        status = self.spotify.get_status()

        self.spotify_update_job = None
        self.project_refresh_job = None

        self.create_widgets()

        self.update_spotify_status()
        self.update_project_card()
        self.auto_refresh_project_card()

    def show(self):

        self.root.mainloop()

        return self.result

    # -------------------------------------------------
    # GUI
    # -------------------------------------------------

    def create_widgets(self):

        ttk.Label(
            self.root,
            text="AbiCut",
            font=("Arial", 24, "bold")
        ).pack(pady=(25, 5))

        ttk.Label(
            self.root,
            text="Projektverwaltung",
            font=("Arial", 11)
        ).pack()

        ttk.Separator(
            self.root,
            orient="horizontal"
        ).pack(fill="x", padx=20, pady=20)

        current_project = get_current_project()

        stats = None

        if current_project:

            try:

                stats = load_project_statistics(
                    current_project
                )

            except Exception as e:

                print(e)

                stats = None

        ttk.Label(

            self.root,

            text="Aktuelles Projekt",

            font=("Arial",12,"bold")

        ).pack(anchor="w", padx=25)

        self.card = ttk.LabelFrame(             # Preview Card mit Projektinformationen und Statistiken
            self.root,
            padding=15
        )

        self.card.pack(
            fill="x",
            padx=25,
            pady=(8,18),
            ipady=8
        )

        # -----------------------------
        # Buttons
        # -----------------------------
        
        ttk.Separator(
            self.root,
            orient="horizontal"
        ).pack(fill="x", padx=20, pady=20)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Neues Projekt",
            width=20,
            command=self.new_project
        ).pack(side="left", padx=6)

        ttk.Button(
            button_frame,
            text="Projekt öffnen",
            width=20,
            command=self.open_project
        ).pack(side="left", padx=6)

        ttk.Button(
            button_frame,
            text="Einstellungen",
            width=20,
            command=self.open_settings
        ).pack(side="left", padx=6)

        ttk.Button(
            button_frame,
            text="Projektmanager",
            width=20,
            command=self.open_project_manager
        ).pack(side="left", padx=6)

        

            
        # -----------------------------
        # Spotify Status
        # -----------------------------

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=25)

        ttk.Label(
            status_frame,
            text="Spotify:"
        ).pack(side="left")

        # LED

        self.status_led = tk.Canvas(
            status_frame,
            width=14,
            height=14,
            highlightthickness=0
        )

        self.status_led.pack(
            side="left",
            padx=(8,4)
        )

        self.led = self.status_led.create_oval(
            2,2,12,12,
            fill="gray"
        )

        # Text

        self.spotify_status = tk.StringVar(
            value="Prüfe Spotify..."
        )

        ttk.Label(
            status_frame,
            textvariable=self.spotify_status
        ).pack(side="left")

    # -------------------------------------------------
    # Buttons
    # -------------------------------------------------

    def new_project(self):

        self.close("wizard")
       

    def open_project(self):

        filename = filedialog.askopenfilename(
            initialdir="projects",
            title="Projekt öffnen",
            filetypes=[
                ("AbiCut Projekt", "*.json")
            ]
        )

        if not filename:
            return

        set_current_project(filename)

        self.result = (
            "editor",
            filename
        )

        self.root.quit()
        self.cleanup()
        self.close(("editor", filename))

    def open_last_project(self):

        config = get_current_project()

        if not config:

            messagebox.showinfo(
                "AbiCut",
                "Kein letztes Projekt vorhanden."
            )

            return

        config = get_current_project()

        self.result = (
            "editor",
            config
        )

        self.root.quit()
        self.cleanup()
        self.root.destroy()

    def open_settings(self):

        SettingsWindow()

    def live_project(self):

        project = get_current_project()

        if not project:
            messagebox.showinfo(
                "AbiCut",
                "Kein Projekt ausgewählt."
            )
            return

        self.result = (
            "live",
            project
        )

        self.root.quit()
        self.cleanup()
        self.root.destroy()

    def update_spotify_status(self):

        status = self.spotify.refresh()

        if status["status"] == "online":

            self.status_led.itemconfig(
                self.led,
                fill="green"
            )

            self.spotify_status.set(
                "Spotify verbunden"
            )

        elif status["status"] == "waiting":

            self.status_led.itemconfig(
                self.led,
                fill="orange"
            )

            self.spotify_status.set(
                "Bitte Spotify öffnen und einen Song starten."
            )

        elif status["status"] == "offline":

            self.status_led.itemconfig(
                self.led,
                fill="red"
            )

            self.spotify_status.set(
                "Keine Spotify-Verbindung."
            )

        else:

            self.status_led.itemconfig(
                self.led,
                fill="red"
            )

            self.spotify_status.set(
                status["text"]
            )

        self.spotify_update_job = self.root.after(
            300,
            self.update_spotify_status
        )

    def update_project_card(self):

        for widget in self.card.winfo_children():
            widget.destroy()

        current_project = get_current_project()

        if not current_project:
            stats = None
        else:
            try:
                stats = load_project_statistics(current_project)
            except:
                stats = None

        if stats:

            progress = create_progress_bar(
                stats["progress"]
            )

            text = (

                f"🎓 {stats['project_name']}\n\n"

                f"Fortschritt:\n"

                f"{progress}   {stats['progress']} %\n\n"

                f"👨‍🎓 Schüler:        {stats['total']}\n"

                f"🎵 Songs:          {stats['songs']}\n"

                f"✅ Bestätigt:      {stats['confirmed']}\n\n"

                f"Erstellt: {stats['created']}"
            )

            ttk.Label(
                self.card,
                text=text,
                justify="left",
                font=("Consolas", 10)
            ).pack(anchor="w")

            button_row = ttk.Frame(self.card)
            button_row.pack(
                anchor="w",
                pady=(20,0)
            )

            ttk.Button(
                button_row,
                text="Editor öffnen",
                width=20,
                command=self.open_last_project
            ).pack(side="left")

            ttk.Button(
                button_row,
                text="Live starten",
                width=20,
                command=self.live_project
            ).pack(side="left", padx=(12,0))

        else:

            ttk.Label(
                self.card,
                text="Noch kein Projekt vorhanden.",
                font=("Arial", 10)
            ).pack(pady=15)

            ttk.Button(
                self.card,
                text="Projekt erstellen",
                command=self.new_project
            ).pack()

    def open_project_manager(self):

        self.close("manager")

    def auto_refresh_project_card(self):

        self.update_project_card()

        self.project_refresh_job = self.root.after(
            3000,
            self.auto_refresh_project_card
        )

    def cleanup(self):

        try:
            if self.spotify_update_job is not None:
                self.root.after_cancel(self.spotify_update_job)
        except:
            pass

        try:
            if self.project_refresh_job is not None:
                self.root.after_cancel(self.project_refresh_job)
        except:
            pass


# -------------------------------------------------

if __name__ == "__main__":

    screen = StartScreen()
    screen.show()