import os
import subprocess

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from settings_manager import load_settings


class SpotifyConnection:

    def __init__(self):

        self.settings = load_settings()

        self.sp = None

        self.connected = False

        self.device = None

        self.error = ""

    # -------------------------

    def connect(self):

        try:

            spotify = self.settings["spotify"]

            self.sp = spotipy.Spotify(

                auth_manager=SpotifyOAuth(

                    client_id=spotify["client_id"],

                    client_secret=spotify["client_secret"],

                    redirect_uri=spotify["redirect_uri"],

                    scope=(
                        "user-read-playback-state "
                        "user-modify-playback-state "
                        "user-read-currently-playing "
                        "playlist-read-private "
                        "playlist-read-collaborative"
                    )

                )

            )

            self.connected = True

            self.error = ""

            return True

        except Exception as e:

            self.connected = False

            self.error = str(e)

            return False

    def find_device(self):

        if not self.connected:

            return None

        try:

            devices = self.sp.devices()["devices"]

            if len(devices) == 0:

                self.device = None

                return None

            self.device = devices[0]

            return self.device

        except:

            self.device = None

            return None

    def test_connection(self):

        if not self.connected:

            return False

        try:

            self.sp.current_user()

            return True

        except:

            return False

    def get_status(self):

        if not self.connected:

            if self.error:

                return {

                    "status": "error",

                    "text": f"Spotify-Authentifizierung fehlgeschlagen: {self.error}"
                }

            return{

                "status": "offline",
                "text": "Keine Spotify-Verbindung."
            }

        if self.find_device():

            return {

                "status": "online",
                "text": f"Spotify verbunden ({self.device['name']})"
            }

        return {

            "status": "waiting",
            "text": "Spotify geöffnet – bitte einen Song starten."
        }

    def reconnect(self):

        self.connected = False

        self.device = None

        return self.connect()

    def refresh(self):

        self.connect()

        return self.get_status()