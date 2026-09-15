import spotipy
from spotipy.oauth2 import SpotifyOAuth

from settings_manager import load_settings

from paths import get_spotify_cache_file


class SpotifyConnection:

    def __init__(self):

        self.settings = load_settings()

        self.sp = None

        self.connected = False

        self.device = None

        self.error = ""

        self._settings_signature = None

    # -------------------------

    def _load_spotify_settings(self):

        self.settings = load_settings()

        spotify = self.settings.get("spotify", {})

        return {
            "client_id": spotify.get("client_id", "").strip(),
            "client_secret": spotify.get("client_secret", "").strip(),
            "redirect_uri": spotify.get("redirect_uri", "").strip()
        }

    def is_configured(self):

        spotify = self._load_spotify_settings()

        return bool(
            spotify["client_id"] and
            spotify["client_secret"] and
            spotify["redirect_uri"]
        )

    def connect(self):

        spotify = self._load_spotify_settings()

        self._settings_signature = (
            spotify["client_id"],
            spotify["client_secret"],
            spotify["redirect_uri"]
        )

        if not all(self._settings_signature):

            self.sp = None
            self.connected = False
            self.device = None
            self.error = ""

            return False

        try:

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
                    ),

                    cache_path=str(get_spotify_cache_file()),
                    open_browser=True

                )

            )

            self.connected = True

            self.error = ""

            return True

        except Exception as e:

            self.sp = None
            self.connected = False
            self.device = None
            self.error = str(e)

            return False

    def find_device(self):

        if not self.connected or self.sp is None:

            return None

        try:

            devices = self.sp.devices()["devices"]

            if len(devices) == 0:

                self.device = None

                return None

            self.device = devices[0]

            return self.device

        except Exception as e:

            self.device = None
            self.connected = False
            self.error = str(e)

            return None

    def test_connection(self):

        if not self.connected or self.sp is None:

            return False

        try:

            self.sp.current_user()

            return True

        except:

            return False

    def get_status(self):

        spotify = self._load_spotify_settings()

        if not all((
            spotify["client_id"],
            spotify["client_secret"],
            spotify["redirect_uri"]
        )):

            return {
                "status": "unconfigured",
                "text": "Spotify nicht konfiguriert – Zugangsdaten in den Einstellungen eintragen."
            }

        if not self.connected:

            if self.error:

                return {

                    "status": "error",

                    "text": f"Spotify-Authentifizierung fehlgeschlagen: {self.error}"
                }

            return {

                "status": "offline",
                "text": "Keine Spotify-Verbindung."
            }

        if self.find_device():

            return {

                "status": "online",
                "text": f"Spotify verbunden ({self.device['name']})"
            }

        if not self.connected and self.error:

            return {
                "status": "error",
                "text": f"Spotify-Authentifizierung fehlgeschlagen: {self.error}"
            }

        return {

            "status": "waiting",
            "text": "Spotify geöffnet – bitte einen Song starten."
        }

    def reconnect(self):

        self.connected = False
        self.device = None
        self.sp = None

        return self.connect()

    def refresh(self):

        spotify = self._load_spotify_settings()

        signature = (
            spotify["client_id"],
            spotify["client_secret"],
            spotify["redirect_uri"]
        )

        if signature != self._settings_signature:

            self.connected = False
            self.device = None
            self.sp = None
            self.error = ""
            self._settings_signature = signature

        if not all(signature):

            return self.get_status()

        if self.sp is None:

            self.connect()

        return self.get_status()
