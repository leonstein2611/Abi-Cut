import json
import spotipy

import tkinter as tk
from tkinter import messagebox

from spotipy.oauth2 import SpotifyOAuth
from settings_manager import get_spotify

from paths import get_app_icon_png

from paths import get_spotify_cache_file

# =========================
# Spotify Setup
# =========================

def get_spotify_client():

    spotify = get_spotify()

    client_id = spotify.get("client_id", "").strip()
    client_secret = spotify.get("client_secret", "").strip()
    redirect_uri = spotify.get("redirect_uri", "").strip()

    if not client_id or not client_secret or not redirect_uri:
        raise RuntimeError(
            "Spotify ist noch nicht konfiguriert. "
            "Bitte Client ID, Client Secret und Redirect URI in den Einstellungen eintragen."
        )

    return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=(
                "user-read-playback-state "
                "user-modify-playback-state "
                "user-read-currently-playing "
                "playlist-read-private "
                "playlist-read-collaborative"
            ),
            cache_path=str(get_spotify_cache_file()),
            open_browser=True
        ))


# =========================
# Playlist Tracks holen
# =========================

def extract_playlist_tracks(playlist_id):

    sp = get_spotify_client()

    results = sp.playlist_items(playlist_id)
    tracks = results["items"]

    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    return tracks


# =========================
# JSON erstellen
# =========================

def import_playlist_to_project(
    playlist_url,
    config_path
):
    try:
        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as f:

            config = json.load(f)

        slides = config["slides"]

        # Playlist-ID bestimmen

        if "playlist/" in playlist_url:

            playlist_id = playlist_url.split("playlist/")[1].split("?")[0]

        else:

            playlist_id = playlist_url

        tracks = extract_playlist_tracks(playlist_id)

        songs_imported = 0

        students_without_song = 0

        playlist_too_long = False

        slide_number = 2

        for item in tracks:

            track = item["track"]

            if not track:
                continue

            slide = slides.get(str(slide_number))

            if slide is None:
                break

            slide["song"] = track["name"]

            slide["artist"] = track["artists"][0]["name"]

            slide["uri"] = track["uri"]

            slide["enabled"] = True

            slide["song_added"] = True

            slide["time_confirmed"] = False

            songs_imported += 1

            slide_number += 1

        for slide in slides.values():

            if slide["song"] == "":

                students_without_song += 1

        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        remaining = len(tracks) - songs_imported

        warning = ""

        if remaining > 0:

            warning = f"""

        ⚠ Nicht importiert:
        {remaining} Songs

        Playlist enthält mehr Songs
        als Schüler.
        """

        root = tk.Tk()

        try:
            icon_path = get_app_icon_png()

            if icon_path.exists():
                app_icon = tk.PhotoImage(file=str(icon_path))
                root.iconphoto(True, app_icon)

        except Exception as e:
            print("Playlist Importer Icon Fehler:", e)

        root.withdraw()
        root.attributes("-topmost", True)

        messagebox.showinfo(

            "AbiCut",

            f"""
        ────────────────────────

        Playlist erfolgreich importiert

        ────────────────────────

        Songs importiert:
        {songs_imported}

        Schüler ohne Song:
        {students_without_song}

        Gesamtfolien:
        {len(slides)}

        {warning}

        ────────────────────────

        Playlist:
        {playlist_id}

        ────────────────────────

        ✓ Songs automatisch den
        entsprechenden Folien zugewiesen.

        ✓ Jetzt können die
        Start- und Endpunkte
        festgelegt werden.

        ────────────────────────
        """
        )
        
    
    except Exception as e:

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        messagebox.showerror(
            "AbiCut",
            f"""
────────────────────────

Playlist konnte nicht importiert werden.

────────────────────────

Bitte prüfen Sie:

• Ist die Playlist öffentlich?

• Ist der Link korrekt?

• Handelt es sich um eine Spotify-Playlist?

────────────────────────

Fehlermeldung:

{e}

────────────────────────
"""
        )

        root.destroy()

        raise
