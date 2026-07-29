# MyAnimeList Metadata Provider for Plex

A Windows-hosted custom metadata provider that brings MyAnimeList anime metadata into modern Plex TV libraries through the Tenrai API.

## Metadata

- Romanised, English, or Japanese titles
- Synopsis, air date, year, runtime, age rating, studios, genres, themes, and demographics
- MAL score displayed as a Plex audience rating
- Default MAL poster plus additional MAL posters
- Default MAL poster assigned as Plex Square Art
- Japanese voice cast by default, with optional fallback to another language
- Character or voice-actor cast thumbnails
- Directors, writers, and producers when MAL positions can be mapped
- Episode titles and air dates

Normal Plex Background art is intentionally left empty so supported clients can use Plex's colour-gradient presentation.

## Easiest Windows installation

1. Download and extract the **Windows release ZIP** from GitHub Releases.
2. Run `INSTALL_AND_START.bat`.
3. Approve the administrator prompt.
4. Add this provider URL in Plex:

```text
http://127.0.0.1:4567/tv
```

The installer starts the provider immediately and registers a Windows Scheduled Task named **MAL Plex Metadata Provider**. It runs under the Windows SYSTEM account whenever the server boots, so no user sign-in is required.

## Settings

Run `EDIT_SETTINGS.bat`, save `settings.json`, then restart the provider task:

```text
STOP_PROVIDER_TASK.bat
START_PROVIDER_TASK.bat
```

The `_help` object inside `settings.json` documents all accepted values and is ignored by the provider.

## Useful files

| File | Purpose |
|---|---|
| `INSTALL_AND_START.bat` | One-click setup, startup registration, and first launch |
| `EDIT_SETTINGS.bat` | Opens `settings.json` |
| `REGISTER_STARTUP.bat` | Adds or repairs the startup Scheduled Task |
| `UNREGISTER_STARTUP.bat` | Removes the startup Scheduled Task |
| `START_PROVIDER_TASK.bat` | Starts the background provider task |
| `STOP_PROVIDER_TASK.bat` | Stops the background provider task |
| `VIEW_LOG.bat` | Opens `logs/provider.log` |
| `TEST_PROVIDER.bat` | Performs a basic provider connectivity test |
| `RUN_PROVIDER.bat` | Runs interactively for troubleshooting |
| `BUILD_EXE.bat` | Builds a standalone Windows EXE with PyInstaller |

## Source installation

The source package requires 64-bit Python 3.12 or newer. Run `INSTALL_AND_START.bat`; it creates `.venv`, installs dependencies, registers the startup task, and starts the provider.

## Manual matching

A MAL ID can be placed in a show-folder name:

```text
Sousou no Frieren [mal-52991]
```

## Logs

Background output is written to:

```text
logs/provider.log
```

## Updating

Stop the provider task, replace the program files while keeping your `settings.json`, then start the task again. Re-run `REGISTER_STARTUP.bat` if the installation folder changes.

## GitHub releases

The included GitHub Actions workflow builds `MALPlexProvider.exe` and creates a ready-to-use Windows ZIP whenever a tag such as `v1.5.0` is pushed. The workflow can also be started manually from the Actions tab.

## Credits

- Metadata: MyAnimeList data through the Tenrai Jikan-compatible API
- Inspiration and feature parity target: Fribb's legacy `MyAnimeList.bundle`

This project is unofficial and is not affiliated with Plex, MyAnimeList, or Tenrai.
