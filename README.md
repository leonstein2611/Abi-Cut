# AbiCut

<p align="center">
  <img src="docs/screenshots/abicut_logo.png" alt="AbiCut Logo" width="650">
</p>

**AbiCut** is a Windows desktop application for preparing and controlling music segments together with PowerPoint slides during live school events.

The project was developed for a real graduation-event workflow: each presentation slide can be assigned to a student and a specific Spotify track segment. AbiCut combines project preparation, Spotify integration, PowerPoint monitoring and a dedicated live view in one application.

## Overview

During a graduation ceremony, individual presentation slides can require a specific part of a song to start at exactly the right moment. Managing this manually becomes difficult when many students, songs and timings have to be coordinated reliably.

AbiCut provides a structured workflow for this process:

1. Create a project from an Excel class list.
2. Optionally import a Spotify playlist.
3. Assign and verify songs for each slide.
4. Define start position, duration and fade settings.
5. Confirm the configuration before the event.
6. Start Live Mode and let AbiCut react to PowerPoint slide changes.

## Application Workflow

### 1. Create a Project

AbiCut starts with a project wizard. A project name, Excel class list and optionally a Spotify playlist can be provided during setup.

![AbiCut Project Wizard](docs/screenshots/new_project.png)

### 2. Import Students

Student names are imported from the selected Excel file. AbiCut detects the relevant name columns and creates the slide structure automatically.

![AbiCut Student Import](docs/screenshots/student_import.png)

### 3. Import a Spotify Playlist

A Spotify playlist can be imported and matched to the generated student slides.

Spotify is optional: AbiCut can be started and used without Spotify credentials. Spotify-dependent features become available after the credentials are configured in the application settings.

![AbiCut Playlist Import](docs/screenshots/playlist_import.png)

### 4. Manage Projects

The main screen and project manager provide an overview of preparation progress and allow existing projects to be opened, duplicated, renamed or deleted.

![AbiCut Startscreen](docs/screenshots/startscreen.png)

![AbiCut Project Manager](docs/screenshots/project_manager.png)

### 5. Configure Music Segments

The editor shows all slides and their preparation state. For each slide, the song, playback position, duration and fade values can be configured and verified.

![AbiCut Editor](docs/screenshots/editor_overview.png)

![AbiCut Slide Editor](docs/screenshots/slide_editor.png)

### 6. Configure Defaults

Default values for start position, song duration and fades can be configured globally.

![AbiCut Settings](docs/screenshots/settings_defaults.png)

### 7. Run the Event

During Live Mode, AbiCut reacts to PowerPoint slide changes and displays the current playback state.

| Unconfigured | Playing | Disabled |
|---|---|---|
| ![](docs/screenshots/live_unconfigured.png) | ![](docs/screenshots/live_playing.png) | ![](docs/screenshots/live_disabled.png) |

## Features

- **Project Wizard**
  - creates a new AbiCut project
  - imports student names from `.xlsx` or `.xls` files
  - automatically detects common name-column formats
  - can import a Spotify playlist directly during setup

- **Project Management**
  - open and manage multiple projects
  - duplicate, rename and delete projects
  - keep track of project preparation progress

- **Spotify Integration**
  - optional Spotify configuration
  - Spotify OAuth authentication
  - persistent local OAuth cache
  - playlist import
  - track metadata retrieval
  - playback control
  - seek to a defined track position
  - automatic fade-in and fade-out

- **Slide Editor**
  - assign songs to individual presentation slides
  - configure start position and playback duration
  - define fade-in and fade-out values
  - test configured track segments
  - enable or disable individual slides
  - explicitly confirm timing configuration

- **PowerPoint Integration**
  - reads the current PowerPoint slideshow position through Windows COM
  - detects slide changes during the presentation
  - reconnects if PowerPoint is opened later
  - handles unavailable or closed presentations without crashing
  - triggers the configured Spotify segment for the active slide

- **Live Monitor**
  - displays the current slide and student
  - shows the active song
  - previews the next slide / student / song
  - displays playback progress and remaining time
  - distinguishes between active, disabled and unconfigured slides
  - indicates PowerPoint connection / slideshow status

- **JSON-based Project Storage**
  - project metadata and slide configuration are stored in readable JSON files
  - each student receives a unique ID
  - configuration states such as `enabled`, `song_added` and `time_confirmed` are stored explicitly

- **Persistent User Data**
  - projects and settings are stored separately from the application files
  - project folders can be copied between PCs
  - application updates do not require moving project data

## Architecture

```text
Excel class list ────────┐
                         │
Spotify playlist ────────┼──> Project Wizard
                         │        │
                         │        v
                         │   Project config (JSON)
                         │        │
                         │        v
                         └──> AbiCut Editor
                                  │
                        ┌─────────┴─────────┐
                        │                   │
                        v                   v
                Spotify Web API      PowerPoint COM
                        │                   │
                        └─────────┬─────────┘
                                  v
                           Live Controller
                                  │
                                  v
                            Live Monitor
```

The application is split into dedicated modules for project management, configuration, Spotify control, PowerPoint communication, editing and live operation.

## Example Project Data

The repository contains:

```text
config.example.json
```

This file documents the current AbiCut project format using fictional names and placeholder Spotify data. It is not automatically loaded as a real project.

A slide entry can contain data such as:

```json
{
  "student": "Max Mustermann",
  "student_id": "example-student-001",
  "song": "Example Song",
  "artist": "Example Artist",
  "uri": "spotify:track:EXAMPLE_TRACK_ID",
  "start_ms": 15000,
  "duration_ms": 30000,
  "fade_in": 2.0,
  "fade_out": 2.0,
  "enabled": true,
  "song_added": true,
  "time_confirmed": true
}
```

Real AbiCut projects are created under:

```text
Documents/
└── AbiCut/
    └── projects/
        └── <project-name>/
            └── config.json
```

This keeps real student and event data outside the public repository.

## Tech Stack

- **Python**
- **Tkinter / ttk** — desktop user interface
- **Spotipy** — Spotify Web API integration
- **Spotify OAuth**
- **pywin32 / win32com** — PowerPoint automation and slideshow monitoring
- **pandas** — Excel class-list import
- **openpyxl / xlrd** — Excel file support
- **JSON** — project and settings storage
- **threading** — playback timing and fades
- **PyInstaller** — Windows application build
- **Inno Setup** — Windows installer packaging

## Requirements

AbiCut currently targets **Windows**, because the PowerPoint integration uses `win32com`.

For the core application you need:

- Python 3
- Microsoft PowerPoint desktop application
- the Python packages listed in `requirements.txt`

Spotify is **not required to start AbiCut**.

To use Spotify-dependent features such as playlist import, song testing and playback control, you additionally need:

- a Spotify developer application
- valid Spotify API credentials
- an available Spotify playback device

## Installation from Source

Clone the repository:

```bash
git clone https://github.com/leonstein2611/abicut.git
cd abicut
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start AbiCut:

```bash
python main.py
```

On first launch, AbiCut creates its local data directory automatically:

```text
Documents/
└── AbiCut/
    ├── settings.json
    ├── current_project.txt
    └── projects/
```

The Spotify OAuth cache is created in the same directory after the first successful Spotify authentication:

```text
Documents\AbiCut\.spotify_cache
```

## Spotify Configuration

Real Spotify credentials are intentionally **not** stored in this repository.

AbiCut can be started normally without Spotify credentials. Spotify-dependent features remain unavailable until credentials are added.

To enable Spotify integration, open the AbiCut settings and enter:

- Spotify Client ID
- Spotify Client Secret
- Redirect URI

The default redirect URI is:

```text
http://127.0.0.1:8888/callback
```

The Spotify application must use the same redirect URI.

AbiCut stores the local settings in:

```text
Documents\AbiCut\settings.json
```

Spotify OAuth authentication is cached locally in:

```text
Documents\AbiCut\.spotify_cache
```

Both files are local runtime data and must not be committed to Git.

## Running AbiCut

Start the application with:

```bash
python main.py
```

AbiCut can be used for project management and preparation without Spotify credentials.

For the full Live Mode workflow:

1. Configure Spotify credentials in AbiCut.
2. Authenticate Spotify once.
3. Make sure a Spotify playback device is active.
4. Open the prepared PowerPoint presentation.
5. Start the PowerPoint slideshow.
6. Open the prepared AbiCut project.
7. Start Live Mode.
8. Changing the PowerPoint slide triggers the corresponding configured Spotify segment.

AbiCut can also reconnect to PowerPoint if the presentation is opened after the application.

## Project Structure

```text
abicut/
├── assets/
│   ├── abicut_logo.png
│   └── abicut_logo.ico
│
├── main.py                  # Application entry point
├── paths.py                 # Application, resource and user-data paths
├── startscreen.py           # Main menu / project overview
├── project_wizard.py        # New-project workflow
├── project_manager.py       # Project management
├── project_controller.py    # Current-project handling
├── project_statistics.py    # Project progress / statistics
├── class_importer.py        # Excel class-list import
├── playlist_importer.py     # Spotify playlist import
├── gui.py                   # Main project editor
├── slide_editor.py          # Detailed slide configuration
├── spotify_connection.py    # Spotify connection / authentication
├── spotify_controller.py    # Spotify playback control
├── powerpoint_controller.py # PowerPoint COM integration
├── live_controller.py       # Live-event logic
├── monitor.py               # Live monitor UI
├── settings_manager.py      # Local settings persistence
├── settings_window.py       # Settings UI
├── baseWindow.py            # Shared window behavior
├── utils.py                 # Time conversion utilities
├── requirements.txt
├── config.example.json
├── version_info.txt
├── AbiCut_Setup.iss
└── .gitignore
```

## Local Data & Privacy

The public repository intentionally excludes runtime and personal data such as:

```text
settings.json
current_project.txt
.spotify_cache
.cache
config.json
projects/
__pycache__/
build/
dist/
installer/
```

This prevents Spotify credentials, authentication data and real student/project information from being published.

User data is stored separately from the application files under:

```text
Documents\AbiCut
```

This separation also allows AbiCut projects to be transferred between PCs by copying the corresponding project folder.

## Windows Build

AbiCut can be packaged as a Windows desktop application using PyInstaller.

Example build command:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onedir --name "AbiCut" --icon "assets\abicut_logo.ico" --version-file "version_info.txt" --add-data "assets;assets" main.py
```

The generated application is located under:

```text
dist\AbiCut\
```

A Windows installer can then be created from the generated `dist\AbiCut` folder using the included `AbiCut_Setup.iss` Inno Setup script.

> The public build must not include real student data or private project folders.

## Project Status

**Version 1.0 — completed / operational**

AbiCut was developed as a complete desktop application for a real school event workflow. The application combines project preparation, validation and live control instead of focusing only on a single playback script.

The current version includes persistent user-data paths, optional Spotify configuration, local OAuth caching, PowerPoint reconnection handling, Windows application branding and installer support.

The public repository documents the technical implementation while keeping credentials and real project data private.

## Background

AbiCut grew from the practical requirement to coordinate PowerPoint slides and individual music segments reliably during a graduation event.

What started as a smaller event-control tool developed into a modular desktop application with project management, Excel and Spotify imports, editing and validation tools, persistent JSON project data and a dedicated Live Controller.

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

## Author

**Leon Stein**

Robotics & Autonomous Systems / technical projects in software, embedded systems and automation.
