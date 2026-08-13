import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from settings_manager import (
    load_settings,
    update_spotify,
    update_defaults
)


class SettingsWindow:

    def __init__(self):

        self.settings = load_settings()

        self.root = tk.Toplevel()
        self.root.title("AbiCut - Einstellungen")
        self.root.geometry("520x420")
        self.root.resizable(False, False)

        self.create_widgets()

    # -------------------------------------------------

    def create_widgets(self):

        ttk.Label(

            self.root,

            text="Einstellungen",

            font=("Arial",18,"bold")

        ).pack(pady=15)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        spotify_tab = ttk.Frame(notebook)
        defaults_tab = ttk.Frame(notebook)

        notebook.add(spotify_tab, text="Spotify")
        notebook.add(defaults_tab, text="Standardwerte")

        # ---------------------------------------
        # Spotify
        # ---------------------------------------

        ttk.Label(
            spotify_tab,
            text="Client ID"
        ).grid(row=0,column=0,sticky="w",padx=10,pady=10)

        self.client_id = tk.StringVar(
            value=self.settings["spotify"]["client_id"]
        )

        ttk.Entry(
            spotify_tab,
            width=45,
            textvariable=self.client_id
        ).grid(row=0,column=1)

        ttk.Label(
            spotify_tab,
            text="Client Secret"
        ).grid(row=1,column=0,sticky="w",padx=10,pady=10)

        self.client_secret = tk.StringVar(
            value=self.settings["spotify"]["client_secret"]
        )

        #Client Secret Entry mit "show" Attribut, um die Eingabe zu verbergen

        self.secret_entry = ttk.Entry(

            spotify_tab,

            width=45,

            textvariable=self.client_secret,

            show="*"

        )

        self.secret_entry.grid(
            row=1,
            column=1
        )

        self.show_secret = tk.BooleanVar(value=False)

        ttk.Checkbutton(

            spotify_tab,

            text="Anzeigen",

            variable=self.show_secret,

            command=self.toggle_secret

        ).grid(row=1,column=2,padx=10)

        ttk.Label(
            spotify_tab,
            text="Redirect URI"
        ).grid(row=2,column=0,sticky="w",padx=10,pady=10)

        self.redirect = tk.StringVar(
            value=self.settings["spotify"]["redirect_uri"]
        )

        ttk.Entry(
            spotify_tab,
            width=45,
            textvariable=self.redirect
        ).grid(row=2,column=1)

        # ---------------------------------------
        # Standardwerte
        # ---------------------------------------

        defaults = self.settings["defaults"]

        ttk.Label(
            defaults_tab,
            text="Startzeit"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=12)

        self.start_ms = tk.IntVar(
            value=defaults["start_ms"]// 1000
        )

        ttk.Entry(
            defaults_tab,
            textvariable=self.start_ms,
            width=15
        ).grid(row=0, column=1)

        ttk.Label(
            defaults_tab,
            text="Songdauer (Sek.)"
        ).grid(row=1,column=0,sticky="w",padx=10,pady=12)

        self.duration = tk.IntVar(
            value=defaults["song_duration"] // 1000  # Konvertiere ms in Sekunden
        )

        ttk.Entry(
            defaults_tab,
            textvariable=self.duration,
            width=15
        ).grid(row=1,column=1)

        ttk.Label(
            defaults_tab,
            text="Fade In (Sek.)"
        ).grid(row=2,column=0,sticky="w",padx=10,pady=12)

        self.fade_in = tk.IntVar(
            value=defaults["fade_in"]
        )

        ttk.Entry(
            defaults_tab,
            textvariable=self.fade_in,
            width=15
        ).grid(row=2,column=1)

        ttk.Label(
            defaults_tab,
            text="Fade Out (Sek.)"
        ).grid(row=3,column=0,sticky="w",padx=10,pady=12)

        self.fade_out = tk.IntVar(
            value=defaults["fade_out"]
        )

        ttk.Entry(
            defaults_tab,
            textvariable=self.fade_out,
            width=15
        ).grid(row=3,column=1)

        ttk.Button(

            self.root,

            text="Speichern",

            command=self.save

        ).pack(pady=15)

    # -------------------------------------------------

    def save(self):

        update_spotify(

            self.client_id.get(),

            self.client_secret.get(),

            self.redirect.get()

        )

        update_defaults(

            self.duration.get() *1000,  # Konvertiere Sekunden in Millisekunden

            self.fade_in.get(),

            self.fade_out.get(),

            self.start_ms.get()*1000

        )

        messagebox.showinfo(

            "AbiCut",

            "Einstellungen gespeichert."

        )

        self.root.destroy()

    def toggle_secret(self):

        if self.show_secret.get():

            self.secret_entry.config(show="")

        else:

            self.secret_entry.config(show="*")