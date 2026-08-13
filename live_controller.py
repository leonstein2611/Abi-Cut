import json
import time

from baseWindow import BaseWindow

from spotify_controller import SpotifyController
from powerpoint_controller import PowerPointController
from monitor import LiveMonitorGUI


class LiveController(BaseWindow):

    def __init__(self, config_path):

        super().__init__()

        # -------------------------
        # Controller
        # -------------------------

        self.spotify = SpotifyController()
        self.powerpoint = PowerPointController()

        # -------------------------
        # Monitor
        # -------------------------

        self.monitor = LiveMonitorGUI()

        # Der Monitor ist jetzt unser Fenster
        self.root = self.monitor.root

        # -------------------------
        # Projekt laden
        # -------------------------

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.slides = self.config["slides"]

        # -------------------------
        # Laufzeitvariablen
        # -------------------------

        self.last_slide = None
        self.current_slide = None

        self.last_change_time = 0

        self.segment_start_ms = 0
        self.segment_duration_ms = 0
        self.segment_end_time = 0

        self.current_status = "WAITING"

        self.MIN_SLIDE_DELAY = 0.4
        self.last_spotify_command = 0

        # -------------------------
        # Fenster schließen
        # -------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.close("menu")
        )

    def show(self):

        self.monitor.update_status(
            status="Warte auf Folie"
        )

        self.monitor.set_led("orange")
        self.monitor.set_status_color("orange")

        self.update()

        return super().show()

    def update(self):

        try:

            if self.check_slide_change():

                self.play_current_slide()

            self.update_progress()

        except Exception as e:

            print("LiveController:", e)

        self.root.after(
            50,
            self.update
        )

    def cleanup(self):

        if self.current_status == "PLAYING":
            self.spotify.stop()

        self.current_status = "STOPPED"

        if hasattr(self.monitor, "cleanup"):
            self.monitor.cleanup()

    def close(self, result=None):

        self.cleanup()

        super().close(result)

    def check_slide_change(self):

        current_slide = self.powerpoint.get_current_slide()

        if current_slide is None:
            return False

        # ---------------------------------
        # Ungültige Werte ignorieren
        # ---------------------------------

        if current_slide <= 0:
            return False

        # ---------------------------------
        # Keine Änderung
        # ---------------------------------

        if current_slide == self.last_slide:
            return False

        # ---------------------------------
        # Entprellung gegen Animationen
        # ---------------------------------

        now = time.time()

        if now - self.last_change_time < self.MIN_SLIDE_DELAY:
            return False

        # ---------------------------------
        # Neue Folie übernehmen
        # ---------------------------------

        self.last_change_time = now

        self.last_slide = current_slide

        self.current_slide = current_slide


        #Debug
        #print(f"Neue Folie: {current_slide}")

        return True

    def play_current_slide(self):

        if time.time() - self.last_spotify_command < 0.3:
            return

        self.last_spotify_command = time.time()

        slide_key = str(self.current_slide)

        # ---------------------------------
        # Folie existiert nicht
        # ---------------------------------

        if slide_key not in self.slides:

            self.show_empty_slide()

            return

        data = self.slides[slide_key]

        if not data.get("enabled", True):

            self.handle_disabled_slide(data)

            return

        self.start_segment(data)

    def handle_disabled_slide(self,data):

        student = data.get("student", "-")
        next_slide = self.current_slide + 1

        if str(next_slide) in self.slides:
        
            next_data = self.slides[str(next_slide)]
        
            next_student = next_data.get("student", "-")
            next_song = next_data.get("song", "-")
        
            next_display = f"{next_slide}"

        else:

            next_display = "Ende"

            next_student = "-"

            next_song = "-"

        if self.current_status == "PLAYING":
            self.spotify.stop()

        self.segment_start_ms = 0
        self.segment_duration_ms = 0
        self.segment_end_time = 0

        self.current_status = "DISABLED"

        self.monitor.set_led("orange")
        self.monitor.set_status_color("orange")

        self.monitor.update_status(
        
            slide=self.current_slide,
        
            student=student,
        
            song="Keine Wiedergabe",
        
            next_slide=next_display,
        
            next_student=next_student,
        
            next_song=next_song,
        
            status="Folie deaktiviert",
        
            segment = (
                f"{self.ms_to_time(data['start_ms'])}  →  "
                f"{self.ms_to_time(data['start_ms'] + data['duration_ms'])}"
            )
        )

        self.monitor.set_progress(0)

        self.monitor.set_remaining_time(0)

    def start_segment(self, data):

        student = data.get("student", "-")

        self.segment_start_ms = data["start_ms"]

        self.segment_duration_ms = data["duration_ms"]

        self.segment_end_time = (
            time.time()
            + self.segment_duration_ms / 1000
        )

        self.current_status = "PLAYING"

        next_slide = self.current_slide + 1

        if str(next_slide) in self.slides:

            next_data = self.slides[str(next_slide)]

            next_student = next_data.get("student", "-")
            next_song = next_data.get("song", "-")

            next_display = f"{next_slide}"

        else:

            next_student = "-"
            next_song = "-"
            next_display = "Ende"

        self.monitor.set_led("limegreen")

        self.monitor.set_status_color("limegreen")

        self.monitor.update_status(

            slide=self.current_slide,

            student=student,

            song=data["song"],

            next_slide=next_display,

            next_student=next_student,

            next_song=next_song,

            status="PLAYING",

            segment = (
                f"{self.ms_to_time(data['start_ms'])}  →  "
                f"{self.ms_to_time(data['start_ms'] + data['duration_ms'])}"
            )
        )

        self.monitor.set_progress(0)

        self.monitor.set_remaining_time(
            self.segment_duration_ms // 1000
        )

        self.spotify.play_segment(

        data["uri"],

        data["start_ms"],

        data["duration_ms"]

    )

    def update_progress(self):

        # ---------------------------------
        # Segment beendet?
        # ---------------------------------

        if (
            self.current_status == "PLAYING"
            and time.time() > self.segment_end_time
        ):

            self.current_status = "FINISHED"
            self.monitor.set_progress(100)

            self.monitor.set_led("orange")
            self.monitor.set_status_color("orange")

            self.monitor.update_status(
                status="Segment beendet"
            )

        # ---------------------------------
        # Nur während Wiedergabe aktualisieren
        # ---------------------------------

        if self.current_status != "PLAYING":
            return

        info = self.spotify.get_current_track_info()

        if not info:
            return

        if self.segment_duration_ms <= 0:
            return

        current_ms = info["progress_ms"]

        segment_end_ms = (
            self.segment_start_ms
            + self.segment_duration_ms
        )

        remaining_seconds = max(
            0,
            int((segment_end_ms - current_ms) / 1000)
        )

        progress = max(
            0,
            min(
                100,
                (
                    (current_ms - self.segment_start_ms)
                    / self.segment_duration_ms
                ) * 100
            )
        )

        seconds = current_ms // 1000

        minutes = seconds // 60

        seconds = seconds % 60

        self.monitor.update_status(

            position=f"{minutes:02}:{seconds:02}"

        )

        self.monitor.set_progress(progress)

        self.monitor.set_remaining_time(remaining_seconds)

    def ms_to_time(self, ms):

        total = ms // 1000

        minutes = total // 60
        seconds = total % 60

        return f"{minutes:02}:{seconds:02}"

    def show_empty_slide(self):

        next_slide = self.current_slide + 1

        if str(next_slide) in self.slides:

            next_data = self.slides[str(next_slide)]

            next_student = next_data.get("student", "-")
            next_song = next_data.get("song", "-")

            next_display = str(next_slide)

        else:

            next_display = "Ende"
            next_student = "-"
            next_song = "-"

        if self.current_status == "PLAYING":
            self.spotify.stop()

        self.current_status = "WAITING"

        self.monitor.set_led("orange")
        self.monitor.set_status_color("orange")

        self.monitor.update_status(

            slide=self.current_slide,

            student="-",

            song="Keine Wiedergabe",

            next_slide=next_display,

            next_student=next_student,

            next_song=next_song,

            status="Keine Konfiguration",

            segment="-"

        )

        self.monitor.set_progress(0)
        self.monitor.set_remaining_time(0)