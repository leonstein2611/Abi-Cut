import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from utils import time_to_ms, ms_to_time
from settings_manager import get_defaults



class SlideEditorWindow(tk.Toplevel):

    def __init__(self, parent, spotify, slide_number=None, slide=None):

        super().__init__(parent)

        self.spotify = spotify
        self.result = None
        self.slide = slide
        self.slide_number = slide_number

        if slide is None:
            self.title("Neue Folie")
        else:
            self.title("Folie bearbeiten")

        self.geometry("650x500")
        self.resizable(False, False)

        defaults = get_defaults()

        self.slide_number_var = tk.StringVar()
        self.student_var = tk.StringVar()

        self.spotify_link_var = tk.StringVar()

        self.song_var = tk.StringVar()
        self.artist_var = tk.StringVar()
        self.uri_var = tk.StringVar()

        self.start_var = tk.StringVar(
            value=ms_to_time(defaults["start_ms"])
        )

        self.duration_var = tk.StringVar(
            value=ms_to_time(defaults["song_duration"])
        )

        self.fadein_var = tk.StringVar(
            value=str(defaults["fade_in"])
        )

        self.fadeout_var = tk.StringVar(
            value=str(defaults["fade_out"])
        )

        self.enabled_var = tk.BooleanVar(value=True)

        self.create_widgets()

        if slide is not None:
            self.load_slide(slide)

    def create_widgets(self):

        padding = 8

        ttk.Label(
            self,
            text="Foliennummer"
        ).grid(row=0,column=0,padx=padding,pady=padding,sticky="w")

        self.slide_number_entry = ttk.Entry(
            self,
            textvariable=self.slide_number_var,
            width=20
        )

        self.slide_number_entry.grid(
            row=0,
            column=1,
            padx=padding,
            sticky="we"
        )

        #Schüler 
        ttk.Label(
            self,
            text="Schüler"
        ).grid(row=1,column=0,padx=padding,pady=padding,sticky="w")

        ttk.Entry(
            self,
            textvariable=self.student_var,
            width=40
        ).grid(row=1,column=1,columnspan=2,sticky="we")
        #Spotify Link
        ttk.Label(
            self,
            text="Spotify Link"
        ).grid(row=2,column=0,padx=padding,pady=padding,sticky="w")

        ttk.Entry(
            self,
            textvariable=self.spotify_link_var,
            width=50
        ).grid(row=2,column=1,sticky="we")

        ttk.Button(
            self,
            text="Song laden",
            command=self.load_song
        ).grid(row=2,column=2,padx=5)
        #Song
        ttk.Label(
            self,
            text="Song"
        ).grid(row=3,column=0,sticky="w",padx=padding)

        ttk.Entry(
            self,
            textvariable=self.song_var,
            state="readonly"
        ).grid(row=3,column=1,columnspan=2,sticky="we")
        #Artist
        ttk.Label(
            self,
            text="Artist"
        ).grid(row=4,column=0,sticky="w",padx=padding)

        ttk.Entry(
            self,
            textvariable=self.artist_var,
            state="readonly"
        ).grid(row=4,column=1,columnspan=2,sticky="we")
        #URI
        ttk.Label(
            self,
            text="URI"
        ).grid(row=5,column=0,sticky="w",padx=padding)

        ttk.Entry(
            self,
            textvariable=self.uri_var,
            state="readonly"
        ).grid(row=5,column=1,columnspan=2,sticky="we")
        # --------------------------
        # Song Einstellungen
        # --------------------------

        ttk.Label(
            self,
            text="Startzeit"
        ).grid(row=6, column=0, padx=padding, pady=padding, sticky="w")

        ttk.Entry(
            self,
            textvariable=self.start_var,
            width=20
        ).grid(row=6, column=1, sticky="we")


        ttk.Label(
            self,
            text="Dauer"
        ).grid(row=7, column=0, padx=padding, pady=padding, sticky="w")

        ttk.Entry(
            self,
            textvariable=self.duration_var,
            width=20
        ).grid(row=7, column=1, sticky="we")


        ttk.Label(
            self,
            text="Fade In"
        ).grid(row=8, column=0, padx=padding, pady=padding, sticky="w")

        ttk.Entry(
            self,
            textvariable=self.fadein_var,
            width=20
        ).grid(row=8, column=1, sticky="we")


        ttk.Label(
            self,
            text="Fade Out"
        ).grid(row=9, column=0, padx=padding, pady=padding, sticky="w")

        ttk.Entry(
            self,
            textvariable=self.fadeout_var,
            width=20
        ).grid(row=9, column=1, sticky="we")


        ttk.Checkbutton(
            self,
            text="Folie aktiviert",
            variable=self.enabled_var
        ).grid(row=10, column=1, sticky="w", pady=10)

        #Standart Werte
        button_frame = ttk.Frame(self)
        button_frame.grid(
            row=20,
            column=0,
            columnspan=3,
            pady=20
        )

        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.destroy
        ).pack(side="left",padx=5)

        ttk.Button(
            button_frame,
            text="Speichern",
            command=self.save
        ).pack(side="left",padx=5)

        # --------------------------
        # Komfortfunktionen
        # --------------------------

        tools = ttk.LabelFrame(
            self,
            text="Werkzeuge"
        )

        tools.grid(
            row=11,
            column=0,
            columnspan=3,
            padx=padding,
            pady=(15,5),
            sticky="ew"
        )

        ttk.Button(
            tools,
            text="Aktuelle Spotify-Position übernehmen",
            command=self.use_current_position
        ).pack(side="left", padx=5, pady=8)

        ttk.Button(
            tools,
            text="Start setzen",
            command=self.set_start_time
        ).pack(side="left", padx=5)

        ttk.Button(
            tools,
            text="Ende setzen",
            command=self.set_end_time
        ).pack(side="left", padx=5)

        ttk.Button(
            tools,
            text="Test Play",
            command=self.test_play
        ).pack(side="left", padx=5)

    def load_song(self):

        old_uri = self.uri_var.get()

        link = self.spotify_link_var.get().strip()

        if not link:

            messagebox.showerror(
                "Fehler",
                "Bitte einen Spotify-Link eingeben."
            )
            return

        uri = self.spotify_link_to_uri(link)

        if uri is None:

            messagebox.showerror(
                "Fehler",
                "Ungültiger Spotify-Link."
            )
            return

        info = self.spotify.get_track_info_from_uri(uri)

        if info is None:

            messagebox.showerror(
                "Fehler",
                "Song konnte nicht geladen werden."
            )
            return

        self.song_var.set(info["song"])
        self.artist_var.set(info["artist"])
        self.uri_var.set(uri)
        self.spotify_link_var.set(link)

        # Nur wenn wirklich ein anderer Song geladen wurde
        if old_uri and old_uri != uri:

            defaults = get_defaults()

            self.start_var.set(
                ms_to_time(defaults["start_ms"])
            )

            self.duration_var.set(
                ms_to_time(defaults["song_duration"])
            )

            self.fadein_var.set(
                str(defaults["fade_in"])
            )

            self.fadeout_var.set(
                str(defaults["fade_out"])
            )

    def spotify_link_to_uri(self, link):

        try:

            if "/track/" not in link:
                return None

            track_id = link.split("/track/")[1].split("?")[0]

            return f"spotify:track:{track_id}"

        except:

            return None

    def uri_to_link(self, uri):

        try:

            track_id = uri.split(":")[-1]

            return f"https://open.spotify.com/track/{track_id}"

        except:

            return ""

    def save(self):

        if not self.slide_number_var.get():

            messagebox.showerror(
                "Fehler",
                "Foliennummer fehlt."
            )
            return

        if not self.uri_var.get():

            messagebox.showerror(
                "Fehler",
                "Bitte zuerst einen Song laden."
            )
            return

        song_changed = False

        if self.slide is not None:

            old_uri = self.slide.get("uri", "")
            new_uri = self.uri_var.get()

            song_changed = old_uri != new_uri

        self.result = {

            "song": self.song_var.get(),
            "artist": self.artist_var.get(),
            "student": self.student_var.get(),
            "uri": self.uri_var.get(),

            "start_ms": time_to_ms(self.start_var.get()),
            "duration_ms": time_to_ms(self.duration_var.get()),

            "fade_in": float(self.fadein_var.get()),
            "fade_out": float(self.fadeout_var.get()),

            "enabled": self.enabled_var.get(),

            "song_added": True,

            "time_confirmed": (
                False
                if song_changed
                else (
                    self.slide.get("time_confirmed", False)
                    if self.slide
                    else False
                )
            )
        }
        self.slide_number = self.slide_number_var.get()

        self.destroy()

    def test_play(self):

        if not self.uri_var.get():
            return

        self.spotify.play_segment(
            self.uri_var.get(),
            time_to_ms(self.start_var.get()),
            time_to_ms(self.duration_var.get()),
            force=True
        )

    def use_current_position(self):

        position = self.spotify.get_current_position()

        if position is None:

            messagebox.showerror(
                "Fehler",
                "Kein laufender Spotify Song."
            )

            return

        self.start_var.set(ms_to_time(position))

    def set_start_time(self):

        position = self.spotify.get_current_position()

        if position is None:
            return

        self.start_var.set(
            ms_to_time(position)
        )

    def set_end_time(self):

        position = self.spotify.get_current_position()

        if position is None:
            return

        start_ms = time_to_ms(
            self.start_var.get()
        )

        duration = max(
            0,
            position - start_ms
        )

        self.duration_var.set(
            ms_to_time(duration)
        )

    def load_slide(self, slide):

        self.slide_number_var.set(self.slide_number)

        self.slide_number_var.set(self.slide_number)

        self.slide_number_entry.config(state="readonly")

        self.student_var.set(
            slide.get("student", "")
        )

        self.song_var.set(
            slide.get("song", "")
        )

        self.artist_var.set(
            slide.get("artist", "")
        )

        self.uri_var.set(
            slide.get("uri", "")
        )

        self.spotify_link_var.set(
            self.uri_to_link(
                slide.get("uri", "")
            )
        )

        self.start_var.set(
            ms_to_time(
                slide.get("start_ms", 0)
            )
        )

        self.duration_var.set(
            ms_to_time(
                slide.get("duration_ms", 30000)
            )
        )

        self.fadein_var.set(
            str(
                slide.get("fade_in", 2)
            )
        )

        self.fadeout_var.set(
            str(
                slide.get("fade_out", 2)
            )
        )

        self.enabled_var.set(
            slide.get("enabled", True)
        )