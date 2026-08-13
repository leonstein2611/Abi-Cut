# =========================
# gui.py
# =========================

import json
import tkinter as tk
import time

from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

from spotify_controller import SpotifyController

from project_controller import get_current_project

from slide_editor import SlideEditorWindow
from utils import ms_to_time, time_to_ms
from baseWindow import BaseWindow


CONFIG_FILE = "config.json"


# =========================
# GUI
# =========================

class MusicGUI(BaseWindow):

    def __init__(self,config_path):

        super().__init__()

        self.result = None

        self.config_path = config_path
        self.config = self.load_config()

        self.spotify = SpotifyController()

        self.user_dragging_slider = False

        self.last_progress_ms = 0
        self.last_update_time = time.time()

        self.root = tk.Tk()
        self.root.title("Abi Music Controller")
        self.root.geometry("1550x720")
       

        self.config = self.load_config()

        self.autosave_enabled = tk.BooleanVar(value=False)
        self.autosave_job = None
        self.spotify_update_job = None

        self.enabled_var = tk.BooleanVar(value=True)

        self.confirmed_var = tk.BooleanVar(value=False)

        self.create_widgets()

        self.bind_shortcuts()

        self.update_spotify_info()

        

    def show(self):

        self.root.mainloop()

        return self.result


    # =========================
    # Config laden
    # =========================

    def load_config(self):

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    
        return config

    # =========================
    # Config speichern
    # =========================

    def save_config(self):

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    # =========================
    # GUI erstellen
    # =========================

    def create_widgets(self):

        # =========================
        # LEFT FRAME
        # =========================

        left_frame = ttk.Frame(self.root)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(
            left_frame,
            text="Folien",
            font=("Arial", 12, "bold")
        ).pack()

        self.slide_tree = ttk.Treeview(
            left_frame,
            columns=("song", "zeit", "aktiv"),
            show="tree headings",
            height=25
        )

        self.slide_tree.heading("#0", text="Folie")
        self.slide_tree.heading("song", text="🎵 Song")
        self.slide_tree.heading("zeit", text="⏱ Zeit")
        self.slide_tree.heading("aktiv", text="Aktiv")

        self.slide_tree.column("#0", width=170)
        self.slide_tree.column("song", width=80, anchor="center")
        self.slide_tree.column("zeit", width=80, anchor="center")
        self.slide_tree.column("aktiv", width=80, anchor="center")

        self.slide_tree.pack(fill="both", expand=True)

        list_button_frame = ttk.Frame(left_frame)
        list_button_frame.pack(fill="x", pady=5)

        ttk.Button(
            list_button_frame,
            text="+ Folie",
            command=self.add_slide
        ).pack(side="left", expand=True, fill="x", padx=2)

        ttk.Button(
            list_button_frame,
            text="Bearbeiten",
            command=self.edit_slide
        ).pack(side="left", expand=True, fill="x", padx=2)

        ttk.Button(
            list_button_frame,
            text="🗑 Löschen",
            command=self.delete_slide
        ).pack(side="left", expand=True, fill="x", padx=2)

        ttk.Button(
            list_button_frame,
            text="⇄ Tauschen",
            command=self.swap_slides
        ).pack(side="left", expand=True, fill="x", padx=2)


        self.refresh_slide_list()

        self.slide_tree.bind(
            "<<TreeviewSelect>>",
            self.on_slide_select
        )

        # =========================
        # RIGHT FRAME
        # =========================

        right_frame = ttk.Frame(self.root)
        right_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        #Hauptmenü button    
        top_frame = ttk.Frame(right_frame)
        top_frame.grid(row=0, column=1, sticky="ne")

        ttk.Button(
            top_frame,
            text="⬅ Hauptmenü",
            command=self.back_to_main_menu
        ).pack()

        self.student_var = tk.StringVar()

        ttk.Label(
            right_frame,
            text="Schüler",
            font=("Arial",10,"bold")
        ).grid(row=8, column=0, sticky="w")

        # =========================
        # LIVE INFO
        # =========================

        self.current_song_var = tk.StringVar(
            value="Kein Song"
        )

        self.current_position_var = tk.StringVar(
            value="00:00.000"
        )
        self.spotify_status_var = tk.StringVar(
            value="Nicht verbunden"
        )

        # Spotify LED

        ttk.Label(
            right_frame,
            text="Spotify",
            font=("Arial",10,"bold")
        ).grid(row=4,column=0,sticky="w")

        spotify_frame = ttk.Frame(right_frame)
        spotify_frame.grid(
            row=5,
            column=0,
            sticky="w",
            pady=(0,20)
        )

        self.spotify_canvas = tk.Canvas(
            spotify_frame,
            width=16,
            height=16,
            highlightthickness=0
        )

        self.spotify_canvas.pack(side="left")

        self.spotify_led = self.spotify_canvas.create_oval(
            2,
            2,
            14,
            14,
            fill="gray"
        )

        ttk.Label(
            spotify_frame,
            textvariable=self.spotify_status_var
        ).pack(side="left", padx=6)

        ttk.Label(
            right_frame,
            text="Aktueller Spotify Song:",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            right_frame,
            textvariable=self.current_song_var
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        ttk.Label(
            right_frame,
            text="Aktuelle Position:",
            font=("Arial", 10, "bold")
        ).grid(row=2, column=0, sticky="w")

        ttk.Label(
            right_frame,
            textvariable=self.current_position_var
        ).grid(row=3, column=0, sticky="w", pady=(0, 15))

        # =========================
        # Segment Visualisierung
        # =========================

        self.segment_canvas = tk.Canvas(
            right_frame,
            height=20,
            bg="#222222",
            highlightthickness=0
        )

        self.segment_canvas.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="we",
            pady=(0, 5)
        )

        # =========================
        # Timeline Slider
        # =========================

        self.timeline_slider = tk.Scale(
            right_frame,
            from_=0,
            to=300,
            orient="horizontal",
            length=400
        )

        self.timeline_slider.grid(
            row=7,
            column=0,
            columnspan=2,
            pady=(0, 20),
            sticky="we"
        )

        # Events
        self.timeline_slider.bind(
            "<ButtonPress-1>",
            self.start_slider_drag
        )

        self.timeline_slider.bind(
            "<ButtonRelease-1>",
            self.stop_slider_drag
        )

        # =========================
        # SONG CONFIG
        # =========================

        ttk.Label(right_frame, text="Song").grid(
            row=9,
            column=0,
            sticky="w"
        )

        self.song_var = tk.StringVar()

        self.song_entry = ttk.Entry(
            right_frame,
            width=60,
            textvariable=self.song_var
        )

        self.song_entry.grid(
            row=9,
            column=1,
            pady=5
        )

        ttk.Label(right_frame, text="Artist").grid(
            row=10,
            column=0,
            sticky="w"
        )

        self.artist_var = tk.StringVar()

        self.artist_entry = ttk.Entry(
            right_frame,
            width=60,
            textvariable=self.artist_var
        )

        self.artist_entry.grid(
            row=10,
            column=1,
            pady=5
        )

        ttk.Label(right_frame, text="URI").grid(
            row=11,
            column=0,
            sticky="w"
        )

        self.uri_var = tk.StringVar()

        self.uri_entry = ttk.Entry(
            right_frame,
            width=60,
            textvariable=self.uri_var
        )

        self.uri_entry.grid(
            row=11,
            column=1,
            pady=5
        )

        ttk.Label(right_frame, text="Startzeit").grid(
            row=12,
            column=0,
            sticky="w"
        )

        self.start_var = tk.StringVar()
        self.start_entry = ttk.Entry(right_frame, textvariable=self.start_var)

        self.start_entry.grid(
            row=12,
            column=1,
            pady=5
        )

        ttk.Label(right_frame, text="Dauer").grid(
            row=13,
            column=0,
            sticky="w"
        )

        self.duration_var = tk.StringVar()
        self.duration_entry = ttk.Entry(right_frame, textvariable=self.duration_var)

        self.duration_entry.grid(
            row=13,
            column=1,
            pady=5
        )

        ttk.Label(right_frame, text="Fade In").grid(
            row=14,
            column=0,
            sticky="w"
        )

        self.fadein_var = tk.StringVar()
        self.fadein_entry = ttk.Entry(right_frame, textvariable=self.fadein_var)

        self.fadein_entry.grid(
            row=14,
            column=1,
            pady=5
        )

        ttk.Label(right_frame, text="Fade Out").grid(
            row=15,
            column=0,
            sticky="w"
        )

        self.fadeout_var = tk.StringVar()
        self.fadeout_entry = ttk.Entry(right_frame, textvariable=self.fadeout_var)

        self.fadeout_entry.grid(
            row=15,
            column=1,
            pady=5
        )

        # =========================
        # Autosave Events
        # =========================

        vars_to_watch = [

            self.song_var,
            self.artist_var,
            self.uri_var,
            self.start_var,
            self.duration_var,
            self.fadein_var,
            self.fadeout_var
        ]

        for var in vars_to_watch:

            var.trace_add(
                "write",
                lambda *args: self.trigger_autosave()
            )

        # =========================
        # BUTTONS
        # =========================

        button_frame = ttk.Frame(right_frame)

        button_frame.grid(
            row=16,
            column=1,
            pady=20
        )

        ttk.Button(
            button_frame,
            text="Save",
            command=self.save_current_slide
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Test Play",
            command=self.test_play
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_music
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Use Current Position",
            command=self.use_current_position
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Set Start",
            command=self.set_start_time
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Set End",
            command=self.set_end_time
        ).pack(side="left", padx=5)

        autosave_checkbox = ttk.Checkbutton(
            button_frame,
            text="Auto Save",
            variable=self.autosave_enabled,
            takefocus=False
        )

        ttk.Checkbutton(
            button_frame,
            text="Folie aktiv",
            variable=self.enabled_var,
            command=self.toggle_slide_enabled
        ).pack(side="left", padx=10)

        ttk.Checkbutton(
            button_frame,
            text="Segment bestätigt",
            variable=self.confirmed_var,
            command=self.toggle_confirmed
        ).pack(side="left", padx=10)


        autosave_checkbox.pack(side="left", padx=10)

        # =========================
        # Erste Folie laden
        # =========================

        children = self.slide_tree.get_children()

        if children:

            self.slide_tree.selection_set(children[0])
            self.on_slide_select(None)

    # =========================
    # Deaktivieren/Aktivieren der Folie
    # =========================


    def toggle_slide_enabled(self):

        if self.current_slide is None:
            return

        self.config["slides"][self.current_slide]["enabled"] = (
            self.enabled_var.get()
        )

        self.save_config()
        self.refresh_slide_list()

    # =========================
    # Folie auswählen
    # =========================

    def on_slide_select(self, event):

        selection = self.slide_tree.selection()

        if not selection:
            return

        self.current_slide = selection[0]

        data = self.config["slides"].get(
            self.current_slide
        )

        if data is None:
            return
        
        start_ms = int(data.get("start_ms", 0))
        duration_ms = int(data.get("duration_ms", 30000))

        self.start_var.set(ms_to_time(start_ms))
        self.duration_var.set(ms_to_time(duration_ms))

        self.enabled_var.set(
            data.get("enabled", True)
        )

        self.confirmed_var.set(
            data.get("time_confirmed", False)
        )

        if not data:
            return

        self.song_var.set(data["song"])

        self.artist_var.set(data["artist"])

        self.uri_var.set(data["uri"])

        self.fadein_var.set(data["fade_in"])

        self.fadeout_var.set(data["fade_out"])
          
        

    # =========================
    # Speichern
    # =========================

    def save_current_slide(self, show_popup=True):

        if not hasattr(self, "current_slide"):
            return

        try:

            fade_in = float(self.fadein_var.get() or 0)
            fade_out = float(self.fadeout_var.get() or 0)

            slide = self.config["slides"][self.current_slide]

            slide["song"] = self.song_var.get()
            slide["artist"] = self.artist_var.get()
            slide["uri"] = self.uri_var.get()
            slide["start_ms"] = time_to_ms(self.start_var.get())
            slide["duration_ms"] = time_to_ms(self.duration_var.get())
            slide["fade_in"] = fade_in
            slide["fade_out"] = fade_out
            slide["enabled"] = bool(self.enabled_var.get())
            slide["song_added"] = bool(self.song_var.get())
            slide["time_confirmed"] = self.confirmed_var.get()

            self.save_config()
            self.refresh_slide_list()

            print("CONFIG GESPEICHERT")

            if show_popup:

                messagebox.showinfo(
                    "Gespeichert",
                    "Config gespeichert"
                )

        except Exception as e:

            print("SAVE ERROR:", e)

    def toggle_confirmed(self):

        if self.current_slide is None:
            return

        self.config["slides"][self.current_slide]["time_confirmed"] = (
            self.confirmed_var.get()
        )

        self.save_config()
        self.refresh_slide_list()
                    
    # =========================
    # Test Play
    # =========================

    def test_play(self):

        uri = self.uri_var.get()

        start_ms = time_to_ms(
            self.start_var.get()
        )

        duration_ms = time_to_ms(
            self.duration_var.get()
        )

        self.spotify.play_segment(
            uri,
            start_ms,
            duration_ms,
            force=True
        )

    # =========================
    # Stop
    # =========================

    def stop_music(self):

        self.spotify.stop()

    # =========================
    # Position übernehmen
    # =========================

    def use_current_position(self):

        position = self.spotify.get_current_position()

        if position is None:

            messagebox.showerror(
                "Fehler",
                "Kein laufender Spotify Song gefunden"
            )

            return

        self.start_var.set(ms_to_time(position))

    # =========================
    # Startzeit setzen
    # =========================

    def set_start_time(self):

        position = self.spotify.get_current_position()

        if position is None:
            return

        self.start_var.set(
            ms_to_time(position)
    )

    # =========================
    # Endzeit setzen
    # =========================

    def set_end_time(self):

        position = self.spotify.get_current_position()

        if position is None:
            return

        start_ms = time_to_ms(
        self.start_var.get()
    )

        duration_ms = position - start_ms

        if duration_ms < 0:
            duration_ms = 0

        self.duration_var.set(ms_to_time(duration_ms))

    def ms_to_display_time(self,ms):

        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60

        return f"{minutes:02}:{seconds:02}"

    # =========================
    # Live Spotify Info
    # =========================

    def update_spotify_info(self):

        info = self.spotify.get_current_track_info()

        if info:

            self.current_song_var.set(
                f"{info['song']} - {info['artist']}"
            )

            current_time = time.time()

            elapsed = (
                current_time -
                self.last_update_time
            ) * 1000

            smooth_progress = int(
                self.last_progress_ms + elapsed
            )

            self.current_position_var.set(
                self.ms_to_display_time(smooth_progress)
            )
    

            duration_ms = info["duration_ms"]
            self.draw_segment_overlay(duration_ms)

            if duration_ms > 0:

                # Slider Länge an Song anpassen
                self.timeline_slider.config(
                    to=duration_ms / 1000
                )

                slider_value = info["progress_ms"] / 1000

                if not self.user_dragging_slider:

                    self.timeline_slider.set(slider_value)

            if info["is_playing"]:

                self.spotify_status_var.set("Wiedergabe aktiv")

                self.spotify_canvas.itemconfig(
                    self.spotify_led,
                    fill="limegreen"
                )

            else:

                self.spotify_status_var.set("Pausiert")

                self.spotify_canvas.itemconfig(
                    self.spotify_led,
                    fill="orange"
                )
            
            self.last_progress_ms = info["progress_ms"]
            self.last_update_time = time.time()

        else:

            self.current_song_var.set("Kein Song")

            self.current_position_var.set("00:00.000")

            self.spotify_status_var.set("Nicht verbunden")

            self.spotify_canvas.itemconfig(
                self.spotify_led,
                fill="red"
            )

        self.spotify_update_job = self.root.after(
            200,
            self.update_spotify_info
        )

    # =========================
    # Segment zeichnen
    # =========================

    def draw_segment_overlay(self, duration_ms):

        self.segment_canvas.update_idletasks()

        self.segment_canvas.delete("all")

        width = self.segment_canvas.winfo_width()

        if width <= 1:
            return

        try:

            start_ms = time_to_ms(
                self.start_var.get()
            )

            segment_duration = time_to_ms(
                self.duration_var.get()
            )

            end_ms = start_ms + segment_duration

        except:
            return

        # Positionen berechnen
        padding = 15

        usable_width = width - (padding * 2)

        start_x = padding + (
            start_ms / duration_ms
        ) * usable_width

        end_x = padding + (
            end_ms / duration_ms
        ) * usable_width

        # Hintergrundlinie
        self.segment_canvas.create_line(
            0,
            10,
            width,
            10,
            fill="#555555",
            width=2
        )

        # Segment
        self.segment_canvas.create_rectangle(
            start_x,
            4,
            end_x,
            16,
            fill="#1D8AB9",
            outline=""
        )

    # =========================
    # Start Marker
    # =========================

        self.segment_canvas.create_line(
            start_x,
            0,
            start_x,
            20,
            fill="#00FF88",
            width=3
        )

    # =========================
    # End Marker
    # =========================

        self.segment_canvas.create_line(
            end_x,
            0,
            end_x,
            20,
            fill="#FF4444",
            width=3
        )

    # =========================
    # Label
    # =========================

        self.segment_canvas.create_text(
            start_x,
            9,
            text="S",
            fill="#00FF88",
            font=("Arial", 10, "bold")
        )

        self.segment_canvas.create_text(
            end_x,
            9,
            text="E",
            fill="#FF4444",
            font=("Arial", 10, "bold")
        )

    # =========================
    # Aktuelle Position
    # =========================

        info = self.spotify.get_current_track_info()

        if info:

            current_ms = info["progress_ms"]

            current_x = padding + (
                current_ms / duration_ms
            ) * usable_width

            self.segment_canvas.create_oval(
                current_x - 5,
                5,
                current_x + 5,
                15,
                fill="white",
                outline=""
            )

    # =========================
    # Slider Drag Start
    # =========================

    def start_slider_drag(self, event):

        self.user_dragging_slider = True

    # =========================
    # Slider Drag Stop
    # =========================

    def stop_slider_drag(self, event):

        self.user_dragging_slider = False

        info = self.spotify.get_current_track_info()

        if not info:
            return

        duration_ms = info["duration_ms"]

        slider_value = self.timeline_slider.get()

        position_ms = int(slider_value * 1000)

        self.spotify.seek_to_position(position_ms)

    # =========================
    # Shortcuts 
    # =========================

    def bind_shortcuts(self):

        self.root.bind(
            "<space>",
            self.handle_space_shortcut
        )

        self.root.bind(
            "s",
            self.handle_s_shortcut
        )

        self.root.bind(
            "e",
            self.handle_e_shortcut
        )

        self.root.bind(
            "<Control-s>",
            lambda event: self.save_current_slide()
        )

        self.root.bind(
            "<Left>",
            self.handle_left_shortcut
        )

        self.root.bind(
            "<Right>",
            self.handle_right_shortcut
        )

        self.root.bind(
            "c",
            self.handle_c_shortcut
        )

    def handle_c_shortcut(self, event):

        if self.typing_in_entry():
            return

        self.confirmed_var.set(
            not self.confirmed_var.get()
        )

        self.toggle_confirmed()

    def typing_in_entry(self):

        widget = self.root.focus_get()

        if not widget:
            return False

        widget_class = widget.winfo_class()

        return widget_class in [
            "Entry",
            "TEntry",
            "Text"
        ]

    def handle_space_shortcut(self, event):

        if self.typing_in_entry():
            return

        self.toggle_play_pause()


    def handle_s_shortcut(self, event):

        if self.typing_in_entry():
            return

        self.set_start_time()


    def handle_e_shortcut(self, event):

        if self.typing_in_entry():
            return

        self.set_end_time()


    def handle_left_shortcut(self, event):

        if self.typing_in_entry():
            return

        self.seek_relative(-1000)


    def handle_right_shortcut(self, event):

        if self.typing_in_entry():
            return

        self.seek_relative(1000)

    # =========================
    # Play/Pause Toggle
    # =========================
    
    def toggle_play_pause(self, event=None):

        info = self.spotify.get_current_track_info()

        if not info:
            return

        if info["is_playing"]:
            self.spotify.stop()
        else:
            self.spotify.resume()

    def seek_relative(self, offset_ms):

        current_time = time.time()

        elapsed = (
            current_time -
            self.last_update_time
        ) * 1000

        current_position = int(
            self.last_progress_ms + elapsed
        )

        new_position = max(
            0,
            current_position + offset_ms
        )

        self.spotify.seek_to_position(
            new_position
        )

        # Lokale Werte sofort updaten
        self.last_progress_ms = new_position
        self.last_update_time = time.time()

    # =========================
    # autosave Funktion
    # =========================

    def trigger_autosave(self):

        if not self.autosave_enabled.get():
            return

        # Alten Timer abbrechen
        if self.autosave_job:
            self.root.after_cancel(self.autosave_job)

        # Neuen Timer starten
        self.autosave_job = self.root.after(
        800,
        lambda: self.save_current_slide(False)
    )

    # =========================
    # Folie hinzufügen
    # ========================= 
    

    def add_slide(self):

        dialog = SlideEditorWindow(
            self.root,
            self.spotify
        )

        self.root.wait_window(dialog)

        if dialog.result is None:
            return

        slide_number = dialog.slide_number

        if slide_number in self.config["slides"]:

            messagebox.showerror(
                "Fehler",
                "Folie existiert bereits."
            )
            return

        self.config["slides"][slide_number] = dialog.result

        self.save_config()

        self.refresh_slide_list()

        messagebox.showinfo(
            "Erfolg",
            f"Folie {slide_number} wurde hinzugefügt."
        )

    def edit_slide(self):

        if not hasattr(self, "current_slide"):
            return

        dialog = SlideEditorWindow(
            self.root,
            self.spotify,
            slide_number=self.current_slide,
            slide=self.config["slides"][self.current_slide]
        )

        self.root.wait_window(dialog)

        if dialog.result is None:
            return

        self.config["slides"][self.current_slide] = dialog.result

        self.save_config()

        self.refresh_slide_list()

        self.slide_tree.selection_set(self.current_slide)

        self.on_slide_select(None)

    def delete_slide(self):

        deleted_slide_number = self.current_slide

        if not hasattr(self, "current_slide"):
            return

        confirm = messagebox.askyesno(
            "Folie löschen",
            f"Folie {self.current_slide} wirklich löschen?"
        )

        if not confirm:
            return

        del self.config["slides"][self.current_slide]

        self.save_config()
        self.refresh_slide_list()

        children = self.slide_tree.get_children()

        if children:
            self.slide_tree.selection_set(children[0])
            self.on_slide_select(None)
        else:
            self.current_slide = None

        messagebox.showinfo(
            "Gelöscht",
            f"Folie {deleted_slide_number} wurde gelöscht."
        )

    def swap_slides(self):

        current = self.current_slide

        if not hasattr(self, "current_slide"):
            return

        target = simpledialog.askstring(
            "Folien tauschen",
            f"Folie {self.current_slide} tauschen mit:"
        )

        if target is None:
            return

        target = target.strip()

        if target == self.current_slide:

            messagebox.showerror(
                "Fehler",
                "Bitte eine andere Folie auswählen."
            )
            return

        if target not in self.config["slides"]:

            messagebox.showerror(
                "Fehler",
                "Diese Folie existiert nicht."
            )
            return

        slides = self.config["slides"]

        slides[self.current_slide], slides[target] = (
            slides[target],
            slides[self.current_slide]
        )

        self.save_config()

        self.refresh_slide_list()

        self.slide_tree.selection_set(target)

        self.on_slide_select(None)

        messagebox.showinfo(
            "Erfolg",
            f"Folie {current} wurde mit Folie {target} getauscht."
        )

        self.slide_tree.selection_set(current)

    def back_to_main_menu(self):

        self.result = "menu"

        self.cleanup()

        self.close("menu")

    def cleanup(self):

        try:
            if self.spotify_update_job is not None:
                self.root.after_cancel(self.spotify_update_job)
        except:
            pass

    #Status der linken Seite 

    def refresh_slide_list(self):

        for item in self.slide_tree.get_children():
            self.slide_tree.delete(item)

        slides = self.config["slides"]

        self.slide_keys = sorted(
            slides.keys(),
            key=int
        )

        for slide_nr in self.slide_keys:

            slide = slides[slide_nr]

            text = (
                f"      "
                f"{int(slide_nr):>3}   "
                f"{slide['student']}"
            )

            song_text, time_text, active_text = self.get_status(slide)

            self.slide_tree.insert(
                "",
                "end",
                iid=slide_nr,
                text=f"{slide_nr}   {slide['student']}",
                values=(
                    song_text,
                    time_text,
                    active_text
                )
            )

    def get_status(self, slide):

        # Song
        if slide.get("song_added", False):
            song_text = "✔ Vorhanden"
        else:
            song_text = "✖ Fehlt"

        # Zeit
        if slide.get("time_confirmed", False):
            time_text = "✔ Bestätigt"
        else:
            time_text = "⏳ Offen"

        # Aktiv
        if slide.get("enabled", True):
            active_text = "✔"
        else:
            active_text = "✖"

        return (
            song_text,
            time_text,
            active_text
        )
    
if __name__ == "__main__":

    config_path = get_current_project()

    MusicGUI(config_path).show()

    