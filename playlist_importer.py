import json
import spotipy

import tkinter as tk
from tkinter import messagebox

from spotipy.oauth2 import SpotifyOAuth
from settings_manager import get_spotify

spotify = get_spotify()

# =========================
# Spotify Setup
# =========================

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify["client_id"],
    client_secret=spotify["client_secret"],
    redirect_uri=spotify["redirect_uri"],
    scope="playlist-read-private playlist-read-collaborative"
))


# =========================
# Playlist Tracks holen
# =========================

def extract_playlist_tracks(playlist_id):

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
