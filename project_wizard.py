import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from class_importer import create_project_from_classlist
from playlist_importer import import_playlist_to_project
from project_controller import set_current_project

from baseWindow import BaseWindow

import subprocess

class ProjectWizard(BaseWindow):

    def __init__(self):

        super().__init__()

        self.root = tk.Tk()

        self.root.title("AbiCut - Neues Projekt")
        self.root.geometry("620x420")
        self.root.resizable(False, False)

        self.project_name = tk.StringVar()
        self.class_file = tk.StringVar()
        self.playlist = tk.StringVar()

        self.skip_playlist = tk.BooleanVar(value=False)
        
        self.create_widgets()


    # ----------------------------------------

    def create_widgets(self):

        ttk.Label(
            self.root,
            text="AbiCut",
            font=("Arial",18,"bold")
        ).pack(pady=(20,5))

        ttk.Label(
            self.root,
            text="Projekt-Assistent"
        ).pack()

        ttk.Separator(
            self.root,
            orient="horizontal"
        ).pack(fill="x", pady=15)

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=25)

        # Projektname

        ttk.Label(
            frame,
            text="Projektname"
        ).grid(row=0, column=0, sticky="w")

        ttk.Entry(
            frame,
            width=45,
            textvariable=self.project_name
        ).grid(
            row=0,
            column=1,
            pady=10
        )

        # Klassenliste

        ttk.Label(
            frame,
            text="Klassenliste"
        ).grid(row=1,column=0,sticky="w")

        ttk.Entry(
            frame,
            width=45,
            textvariable=self.class_file,
            state="readonly"
        ).grid(row=1,column=1)

        ttk.Button(
            frame,
            text="Auswählen",
            command=self.select_class_file
        ).grid(row=1,column=2,padx=10)

        # Playlist

        ttk.Label(
            frame,
            text="Spotify Playlist"
        ).grid(row=2,column=0,sticky="w")

        self.playlist_entry = ttk.Entry(
            frame,
            width=45,
            textvariable=self.playlist
        )

        self.playlist_entry.grid(
            row=2,
            column=1
        )

        ttk.Checkbutton(
            frame,
            text="Später importieren",
            variable=self.skip_playlist,
            command=self.toggle_playlist
        ).grid(row=3,column=1,sticky="w",pady=8)

        ttk.Separator(
            self.root,
            orient="horizontal"
        ).pack(fill="x", pady=20)

        ttk.Button(
            self.root,
            text="Projekt erstellen",
            command=self.create_project
        ).pack(pady=10)

        self.toggle_playlist()

    # ----------------------------------------

    def select_class_file(self):

        filename = filedialog.askopenfilename(

            filetypes=[
                ("Excel","*.xlsx"),
                ("Excel","*.xls")
            ]

        )

        if filename:

            self.class_file.set(filename)

    # ----------------------------------------

    def toggle_playlist(self):

        if self.skip_playlist.get():

            self.playlist.set("")

            self.playlist_entry.config(state="disabled")

        else:

            self.playlist_entry.config(state="normal")

    # ----------------------------------------

    def create_project(self):

        if self.project_name.get() == "":

            messagebox.showerror(
                "Fehler",
                "Bitte Projektname eingeben."
            )
            return

        if self.class_file.get() == "":

            messagebox.showerror(
                "Fehler",
                "Bitte Klassenliste auswählen."
            )
            return

        try:

            config_path = create_project_from_classlist(

            excel_file=self.class_file.get(),

            project_name=self.project_name.get()

        )

            # Playlist direkt importieren
            if not self.skip_playlist.get():

                if self.playlist.get() == "":

                    messagebox.showerror(
                        "Fehler",
                        "Bitte eine Playlist eingeben."
                    )
                    return

                import_playlist_to_project(
                    self.playlist.get(),
                    config_path
                )

            messagebox.showinfo(

                "AbiCut",

                "Projekt erfolgreich erstellt."

            )

            # AbiCut Editor starten
            set_current_project(config_path)

            self.close(("editor", config_path))

        except Exception as e:

            messagebox.showerror(

                "Fehler",

                str(e)

    )


if __name__ == "__main__":
    wizard = ProjectWizard()
    wizard.show()