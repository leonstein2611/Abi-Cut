# =========================
# spotify_controller.py
# =========================

import time
import threading
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from settings_manager import get_spotify

spotify = get_spotify()


class SpotifyController:

    def __init__(self):

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=spotify["client_id"],
            client_secret=spotify["client_secret"],
            redirect_uri=spotify["redirect_uri"],
            scope="user-modify-playback-state user-read-playback-state"
        ))

        self.last_uri = None
        self.last_start_ms = None
        self.last_play_time = 0
        self.fade_lock = threading.Lock()
        self.playback_session = 0

    # =========================
    # Device holen
    # =========================

    def get_device_id(self):

        devices = self.sp.devices()

        if not devices["devices"]:
            return None

        for device in devices["devices"]:
            if device["is_active"]:
                return device["id"]

        return devices["devices"][0]["id"]

    # =========================
    # Lautstärke setzen
    # =========================

    def set_volume(self, volume):

        try:
            self.sp.volume(volume)
        except:
            pass

    # =========================
    # Fade In
    # =========================

    def fade_in(self, target_volume=100, duration=2):

        with self.fade_lock:

            steps = 10
            delay = duration / steps

            for volume in range(
                0,
                target_volume + 1,
                int(target_volume / steps)
            ):

                self.set_volume(volume)
                time.sleep(delay)

    # =========================
    # Fade Out
    # =========================

    def fade_out(self, start_volume=100, duration=2):

        with self.fade_lock:

            steps = 10
            delay = duration / steps

            for volume in range(
                start_volume,
                -1,
                -int(start_volume / steps)
            ):

                self.set_volume(volume)
                time.sleep(delay)

    # =========================
    # Segment abspielen
    # =========================

    def play_segment(
        self,
        uri,
        start_ms,
        duration_ms,
        force=False
    ):
        self.playback_session += 1

        current_session = self.playback_session
        current_time = time.time()

        # Doppeltrigger verhindern
        if (
            not force and
            uri == self.last_uri and
            current_time - self.last_play_time < 1.5
        ):

            print("Spotify Trigger blockiert")
            return

        self.last_uri = uri
        self.last_start_ms = start_ms
        self.last_play_time = current_time

        try:

            device_id = self.get_active_device()

            if not device_id:
                print("Kein Spotify Device aktiv")
                return

            self.sp.start_playback(
                device_id=device_id,
                uris=[uri],
                position_ms=start_ms
            )

            print("Spotify gestartet")

            time.sleep(0.2)
            self.set_volume(0)

            threading.Thread(
                target=self.fade_in,
                args=(100, 2),
                daemon=True
            ).start()

            # Auto Pause Thread starten
            threading.Thread(
                target=self.auto_pause,
                args=(duration_ms, current_session),
                daemon=True
            ).start()

        except Exception as e:

            print("Spotify Fehler:", e)

    def get_active_device(self):

        devices = self.sp.devices()

        for device in devices["devices"]:

            if device["is_active"]:
                return device["id"]

        return None

    # =========================
    # Auto Pause
    # =========================

    def auto_pause(self, duration_ms, session_id):

        fade_duration = 2

        wait_time = (duration_ms / 1000) - fade_duration

        if wait_time > 0:
            time.sleep(wait_time)

        # Wurde inzwischen neuer Song gestartet?
        if session_id != self.playback_session:
            return

        self.fade_out(100, fade_duration)

        # Erneut prüfen
        if session_id != self.playback_session:
            return

        try:
            self.sp.pause_playback()
        except:
            pass

    # =========================
    # Stop
    # =========================

    def stop(self):

        try:

            info = self.get_current_track_info()

            if info:
                self.sp.pause_playback()

        except Exception as e:

            if "403" in str(e):
                return

            print(e)

    # =========================
    # Aktuelle Position
    # =========================

    def get_current_position(self):

        playback = self.sp.current_playback()

        if playback:

            return playback["progress_ms"]

        return None

    # =========================
    # Aktuelle Song Infos
    # =========================

    def get_current_track_info(self):

        playback = self.sp.current_playback()

        if playback and playback["item"]:

            track = playback["item"]

            return {
                "song": track["name"],
                "artist": track["artists"][0]["name"],
                "progress_ms": playback["progress_ms"],
                "duration_ms": track["duration_ms"],
                "is_playing": playback["is_playing"]
            }

        return None

    def get_track_info_from_uri(self, uri):

        try:

            track = self.sp.track(uri)

            return {

                "song": track["name"],
                "artist": track["artists"][0]["name"],
                "duration_ms": track["duration_ms"]

            }

        except Exception as e:

            print("Track Info Fehler:", e)

            return None
        
    def seek_to_position(self, position_ms):

        try:

            self.sp.seek_track(position_ms)

        except:
            pass
    
    def resume(self):

        try:
            self.sp.start_playback()
        except:
            pass