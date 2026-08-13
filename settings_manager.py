import json
import os

SETTINGS_FILE = "settings.json"


DEFAULT_SETTINGS = {

    "spotify": {

        "client_id": "",

        "client_secret": "",

        "redirect_uri":
        "http://127.0.0.1:8888/callback"

    },

    "defaults": {

        "song_duration": 30000,

        "fade_in": 2,

        "fade_out": 2,

        "start_ms": 0

    }
}


def load_settings():

    if not os.path.exists(SETTINGS_FILE):

        save_settings(DEFAULT_SETTINGS)

        return DEFAULT_SETTINGS

    with open(

        SETTINGS_FILE,

        "r",

        encoding="utf-8"

    ) as f:

        return json.load(f)


def save_settings(settings):

    with open(

        SETTINGS_FILE,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            settings,

            f,

            indent=4,

            ensure_ascii=False

        )


def get_spotify():

    return load_settings()["spotify"]


def get_defaults():

    return load_settings()["defaults"]


def update_spotify(

    client_id,

    client_secret,

    redirect_uri

):

    settings = load_settings()

    settings["spotify"] = {

        "client_id": client_id,

        "client_secret": client_secret,

        "redirect_uri": redirect_uri

    }

    save_settings(settings)


def update_defaults(

    duration,

    fade_in,

    fade_out,

    start_ms

):

    settings = load_settings()

    settings["defaults"] = {

        "song_duration": duration,

        "fade_in": fade_in,

        "fade_out": fade_out,

        "start_ms": start_ms

    }

    save_settings(settings)