# MyAnimeList Plex Metadata Provider

A modern MyAnimeList metadata provider for Plex Media Server.

This project provides anime metadata through Plex’s Custom Metadata Provider system and is intended as a modern replacement for the legacy [`MyAnimeList.bundle`](https://github.com/Fribb/MyAnimeList.bundle) plugin.

Metadata is retrieved from MyAnimeList-compatible data supplied through the Tenrai API.

> [!IMPORTANT]
> Plex Custom Metadata Providers are still evolving. Some metadata fields may display differently between Plex Web, Plex Desktop, iOS, Android, Apple TV, Android TV, and other Plex clients.

---

## Features

- MyAnimeList anime search and matching
- Default, English, or Japanese series titles
- Original Japanese series title where supported by Plex
- Anime synopsis
- MAL score
- Release date and year
- Content rating
- Episode titles
- Configurable default, English, Japanese, or romanji episode titles
- Episode synopses when available
- Episode scores converted from MAL’s 5-point scale to Plex’s 10-point scale
- Episode air dates
- Episode runtime
- Genres
- Themes
- Demographics
- Studios
- Japanese voice actors preferred by default
- Fallback voice actors when Japanese cast data is unavailable
- Character or voice-actor profile images
- Director, writer, and producer credits where available
- Default MAL poster
- Additional MAL posters in the Plex artwork picker
- MAL poster assigned as Plex Square Art
- Background artwork disabled by default
- User-editable settings
- Standalone Windows executable
- One-click Windows installation
- Automatic startup using Windows Task Scheduler
- Provider health checks and logging
- Client-side Tenrai API rate limiting and automatic HTTP 429 retries

---

## Known limitations

- Plex Custom Metadata Provider support is still evolving, and behaviour can differ between Plex clients.
- Ratings from custom providers can display correctly but may remain unavailable for library sorting.
- Local TV extras are not reliably detected when this provider is used as the primary metadata agent.
- Plex may ignore `Shorts`, `Other`, `Trailers`, and similar local-extra folders even when their structure follows Plex’s documented naming rules.
- Adding Plex Personal Media or Plex Local Media as a secondary provider does not make ignored extra files appear, because file discovery happens before metadata providers are applied.
- The provider’s `/extras` endpoint intentionally returns an empty container. Remote YouTube trailers and other provider-supplied extras are not currently supported.
- Files that must appear in Plex should be named as normal episodes or specials, such as `S00E01`, or exposed through Plex-compatible hardlinks.
- MyAnimeList usually treats each sequel or season as a separate anime entry, while Plex normally groups seasons under one show. This provider follows the MyAnimeList model.
- Openings, endings, creditless videos, interviews, and disc bonuses usually have no corresponding MyAnimeList episode record.
- Plex may generate unrelated recommendations under Related Shows.
- Existing artwork can remain cached after provider changes.
- MyAnimeList does not provide purpose-built Plex Square Art, so the default poster is reused.
- Staff-role names do not always map cleanly to Plex’s Director, Writer, and Producer fields.
- Original Japanese titles may not be displayed by every Plex client.


---


---

## Credits

This project was inspired by the original:

### [Fribb/MyAnimeList.bundle](https://github.com/Fribb/MyAnimeList.bundle)

The original plugin provided MyAnimeList metadata through Plex’s older plugin and metadata-agent framework.

This project aims to provide similar metadata coverage using Plex’s newer HTTP-based Custom Metadata Provider system.

The implementation in this repository is designed for the modern provider API and does not require the legacy Plex plugin framework.

---

## Quick installation

1. Download the latest Windows release ZIP.
2. Extract the ZIP to a permanent folder, for example:

```text
C:\MAL-Plex-Provider-Windows
```

3. Right-click `INSTALL_AND_START.bat`.
4. Select **Run as administrator**.
5. Wait for the health check to complete.
6. Add the provider to Plex using the instructions below.

The installer registers the provider as a Windows Scheduled Task so it starts automatically whenever the server starts.

The scheduled task is named:

```text
MAL Plex Metadata Provider
```

The provider runs under the Windows `SYSTEM` account and does not require a user to sign in after restarting the server.

---

## Adding the provider to Plex

1. Open **Plex Web**.

2. Go to:

   **Settings → Metadata Agents**

3. Under **Custom Metadata Providers**, select **Add Provider**.

4. Enter the provider URL:

   ```text
   http://127.0.0.1:4567/tv
   ```

5. Save the provider.

6. On the same **Metadata Agents** page, scroll down to the metadata agent configurations.

7. Create a new metadata agent.

8. Give it a name, for example:

   ```text
   MAL Agent
   ```

9. Set **Primary Agent** to:

   ```text
   MyAnimeList Plex Metadata Provider
   ```

10. Save the metadata agent.

11. Go to:

    **Settings → Manage → Libraries**

12. Create or edit a **TV Shows** library.

13. Select the metadata agent you created, for example:

    ```text
    MAL Agent
    ```

14. Save the library.

> [!NOTE]
> Existing shows previously matched with another metadata agent may need to be manually rematched or have their metadata refreshed before they use the MyAnimeList provider.


---

## Force matching with a MyAnimeList ID

If Plex finds the wrong series, or a normal title search does not return the correct result, you can force the provider to match a specific MyAnimeList entry.

Open the series in Plex, choose **Fix Match** or **Match**, and enter the MAL ID using this format:

```text
[mal-52991]
```

Replace `52991` with the series ID from its MyAnimeList URL.

For example, this MyAnimeList URL:

```text
https://myanimelist.net/anime/52991/
```

uses:

```text
[mal-52991]
```

The provider also recognises these formats:

```text
mal-show-52991
```

```text
myanimelist://52991
```

A bare number such as `52991` is not treated as a force-match request.

You can also include the tag permanently in the series folder name:

```text
Sousou no Frieren [mal-52991]
```

This can help Plex identify the correct entry during future scans or rematches.


---

## Configuration

Run:

```text
EDIT_SETTINGS.bat
```

This opens `settings.json` in Notepad.

After changing a setting:

1. Save `settings.json`.
2. Restart the provider.
3. Refresh or rematch the affected series in Plex.

Settings are read when the provider starts. Editing the file while the provider is running does not immediately apply the changes.

---

## Settings reference

### Title and cast settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `title_language` | `"default"` | `"default"`, `"english"`, `"japanese"` | Selects which MyAnimeList title is used as the main Plex series title. `default` normally uses the primary romanised MAL title. |
| `episode_title_language` | `"default"` | `"default"`, `"english"`, `"japanese"`, `"romanji"` | Selects which Tenrai/MAL episode title is used in Plex. Falls back to another available title when the preferred language is unavailable. |
| `voice_actor_language` | `"Japanese"` | `"Japanese"`, `"English"`, `"French"`, `"German"`, `"Spanish"`, `"Italian"`, `"Portuguese"`, `"Korean"`, `"Mandarin"` | Selects the preferred voice-actor language. Japanese is used by default. |
| `voice_actor_fallback` | `true` | `true`, `false` | When enabled, the first available voice actor is used when no actor exists in the preferred language. |
| `cast_image` | `"character"` | `"character"`, `"voice actor"` | Selects whether Plex cast thumbnails display the anime character image or the voice actor’s profile image. |
| `include_cast` | `true` | `true`, `false` | Enables character and voice-actor metadata. |

### Staff settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `include_directors` | `true` | `true`, `false` | Adds staff members whose MAL position is recognised as a director role. |
| `include_writers` | `true` | `true`, `false` | Adds staff members whose MAL position is recognised as a writing, script, composition, or screenplay role. |
| `include_producers` | `true` | `true`, `false` | Adds staff members whose MAL position is recognised as a producer role. |

MAL staff positions are not always standardised. Some people may not be imported when their role does not clearly map to a Plex credit type.

### Classification settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `include_genres` | `true` | `true`, `false` | Imports standard MAL genres such as Comedy, Romance, Drama, or Action. |
| `include_themes` | `true` | `true`, `false` | Imports MAL themes such as School, Music, or Historical as Plex genres. |
| `include_demographics` | `true` | `true`, `false` | Imports demographics such as Shounen, Shoujo, Seinen, or Josei as Plex genres. |
| `include_studios` | `true` | `true`, `false` | Imports the anime studio into the Plex Studio field. |

### Episode settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `include_episode_synopses` | `true` | `true`, `false` | Imports episode synopsis text from Tenrai when available. |
| `episode_synopsis_fallback_requests` | `false` | `true`, `false` | When enabled, requests each individual episode if the paginated episode record has no synopsis. This is disabled by default because Tenrai normally includes synopsis text in the episode list. |
| `include_episode_scores` | `true` | `true`, `false` | Imports MAL episode scores. MAL’s 5-point value is doubled before being sent to Plex’s 10-point rating field. |

### Tenrai API rate-limit settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `tenrai_requests_per_second` | `3` | `1`–`4` | Maximum Tenrai requests started per second across all provider threads. |
| `tenrai_requests_per_minute` | `90` | `1`–`120` | Rolling one-minute request limit. The conservative default leaves room below Tenrai’s public limit. |
| `tenrai_retry_attempts` | `3` | `0`–`10` | Number of retries after HTTP 429 responses or temporary connection failures. |
| `tenrai_retry_default_seconds` | `30` | `1`–`300` | Wait time used when Tenrai returns HTTP 429 without a valid `Retry-After` header. |
| `tenrai_retry_temporary_403` | `true` | `true`, `false` | Treats likely temporary HTTP 403 responses as an IP cooldown or edge-rate-limit response and retries them. |
| `tenrai_retry_forbidden_seconds` | `60` | `1`–`600` | Default wait for a temporary HTTP 403 when no valid `Retry-After` header is supplied. |

The limiter is global and thread-safe, so simultaneous Plex refresh requests share the same request budget. When Tenrai returns HTTP `429`, the provider honors `Retry-After` when supplied and pauses before retrying. Likely temporary HTTP `403` responses are also logged with a compact response-body preview and retried using a longer cooldown.

### Artwork settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `include_additional_posters` | `true` | `true`, `false` | Adds additional MAL images to the Plex Poster artwork picker. |
| `poster_as_square_art` | `true` | `true`, `false` | Makes the default MAL poster available as Plex Square Art. This is particularly useful for current Plex mobile applications. |
| `include_background` | `false` | `true`, `false` | Enables or disables normal Plex background artwork. Backgrounds are disabled by default so Plex can use its colour-gradient interface. |

The default artwork mapping is:

| Plex artwork type | Source |
|---|---|
| Poster | Default MyAnimeList poster |
| Square Art | Default MyAnimeList poster |
| Background | Not supplied by default |
| Additional Posters | Additional images from MyAnimeList |

The MAL poster is vertical rather than square. Plex controls how the image is cropped when displaying it as Square Art.

### Rating settings

| Setting | Default | Accepted values | Description |
|---|---:|---|---|
| `rating_source` | `"tmdb"` | `"tmdb"`, `"imdb"` | Selects one audience-rating icon for both series and episode MAL scores. The numeric rating still comes from MyAnimeList. |

For example:

```json
"rating_source": "tmdb"
```

This causes Plex to display both series and episode MAL scores using Plex’s TMDB-style audience-rating badge.

The score itself still comes from MyAnimeList.

---

## Example settings file

```json
{
  "title_language": "default",
  "episode_title_language": "default",
  "voice_actor_language": "Japanese",
  "voice_actor_fallback": true,
  "cast_image": "character",
  "include_cast": true,
  "include_directors": true,
  "include_writers": true,
  "include_producers": true,
  "include_genres": true,
  "include_themes": true,
  "include_demographics": true,
  "include_studios": true,
  "include_episode_synopses": true,
  "episode_synopsis_fallback_requests": false,
  "include_episode_scores": true,
  "include_additional_posters": true,
  "poster_as_square_art": true,
  "include_background": false,
  "rating_source": "tmdb",
  "tenrai_requests_per_second": 3,
  "tenrai_requests_per_minute": 90,
  "tenrai_retry_attempts": 3,
  "tenrai_retry_default_seconds": 30,
  "tenrai_retry_temporary_403": true,
  "tenrai_retry_forbidden_seconds": 60
}
```

---


## Episode metadata

Episode titles can be selected independently from the main series title using:

```json
"episode_title_language": "default"
```

Accepted values are:

```text
default
english
japanese
romanji
```

The provider imports episode synopsis text directly from Tenrai’s paginated episode response when available.

Individual episode fallback requests are disabled by default:

```json
"episode_synopsis_fallback_requests": false
```

This avoids one additional API request for every episode without a synopsis. Enable it only when testing incomplete episode records.

MAL episode ratings use a five-point scale. The provider converts them to Plex’s ten-point scale:

```text
MAL 4.6 / 5 → Plex 9.2 / 10
```


---

## Voice-actor selection

For each character, the provider uses the following process:

1. Find voice actors listed for the character.
2. Look for an actor matching `voice_actor_language`.
3. Use that actor when available.
4. When no preferred-language actor exists and `voice_actor_fallback` is enabled, use the first available actor.
5. When fallback is disabled, omit that cast entry if no preferred-language actor exists.

Default behaviour:

```json
"voice_actor_language": "Japanese",
"voice_actor_fallback": true
```

This means Japanese actors are preferred, while characters without Japanese cast data can still appear using another available voice actor.

---

## Included files

### End-user files

| File | Purpose |
|---|---|
| `MALPlexProvider.exe` | Standalone provider application. |
| `settings.json` | User configuration file. |
| `INSTALL_AND_START.bat` | Registers startup, starts the provider, and performs a health check. |
| `EDIT_SETTINGS.bat` | Opens `settings.json` in Notepad. |
| `REGISTER_STARTUP.bat` | Registers the Windows Scheduled Task. |
| `UNREGISTER_STARTUP.bat` | Removes the Windows Scheduled Task. |
| `START_PROVIDER_TASK.bat` | Starts the registered provider task. |
| `STOP_PROVIDER_TASK.bat` | Stops the registered provider task. |
| `TEST_PROVIDER.bat` | Performs a basic provider connection test. |
| `VIEW_LOG.bat` | Opens the provider log. |

### Development files

| File | Purpose |
|---|---|
| `app.py` | Main Python provider application. |
| `requirements.txt` | Python dependencies. |
| `setup.bat` | Creates the Python virtual environment and installs dependencies. |
| `START_PROVIDER.bat` | Runs the provider from Python source. |
| `BUILD_EXE.bat` | Builds the standalone Windows executable using PyInstaller. |
| `.github/workflows/build-windows.yml` | GitHub Actions workflow for Windows release builds. |

---

## Provider URLs

Provider registration URL:

```text
http://127.0.0.1:4567/tv
```

Health check:

```text
http://127.0.0.1:4567/health
```

Default port:

```text
4567
```

---

## Starting and stopping the provider

Start the registered provider task:

```text
START_PROVIDER_TASK.bat
```

Stop it:

```text
STOP_PROVIDER_TASK.bat
```

Register or repair automatic startup:

```text
REGISTER_STARTUP.bat
```

Remove automatic startup:

```text
UNREGISTER_STARTUP.bat
```

Administrative permission may be required when modifying the Scheduled Task.

---

## Logs

Provider logs are stored in:

```text
logs\provider.log
```

Run:

```text
VIEW_LOG.bat
```

to open the log.

The log includes:

- Provider startup
- Loaded settings
- Plex metadata requests
- Tenrai API requests
- HTTP status codes
- Metadata errors
- Artwork requests
- Health-check requests

> [!WARNING]
> Do not publicly post logs without checking them for private paths, filenames, server details, or Plex authentication tokens.

---

## Testing the provider

Run:

```text
TEST_PROVIDER.bat
```

This checks whether the local provider is reachable.

You may also open the health endpoint in a browser:

```text
http://127.0.0.1:4567/health
```

A successful response confirms that the provider process is running.

It does not necessarily confirm that Plex has registered the provider correctly or that every external metadata request is working.

---

## Building from source

### Requirements

- Windows 10 or Windows 11
- Python 3
- Internet access during dependency installation
- Plex Media Server with Custom Metadata Provider support

Run:

```text
setup.bat
```

Then start the provider:

```text
START_PROVIDER.bat
```

To build a standalone executable:

```text
BUILD_EXE.bat
```

The executable is created at:

```text
dist\MALPlexProvider.exe
```

---

## Troubleshooting

### Tenrai returns HTTP 403

A Tenrai `403` can indicate a temporary IP-level block or edge-rate-limit response rather than a normal application error.

The provider now:

- logs a compact response-body preview;
- records useful headers such as `Server`, `Content-Type`, and `Retry-After`;
- retries likely temporary `403` responses;
- waits 60 seconds by default between retries;
- returns HTTP `503` to Plex for temporary upstream failures instead of a generic `500`.

When the log says the IP is temporarily refused, stop refreshing and allow the cooldown to expire.

---

### Tenrai reports that the rate limit was exceeded

The provider automatically limits outgoing Tenrai requests and retries HTTP `429` responses. Check the log for entries such as:

```text
Tenrai client rate limiter waiting
Tenrai returned HTTP 429; waiting
```

Avoid raising the configured limits above Tenrai’s published maximums. The defaults of `3` requests per second and `90` requests per minute are intentionally conservative.

---

### Plex requests the extras endpoint

Plex may probe `/extras` during a metadata refresh even though this provider does not supply trailers or other extras. The provider returns a valid empty metadata container with HTTP `200`; this is normal.

Local TV extras are a separate scanner-level feature. In testing, files placed under supported folders such as:

```text
Shorts
Other
Trailers
Interviews
Featurettes
```

were not reliably detected when the MyAnimeList provider was used as the primary metadata agent, even with simple filenames and documented folder placement.

Adding Plex Personal Media or Plex Local Media as a secondary provider does not correct this because secondary providers cannot create items that Plex’s scanner has already ignored.

For files that must appear in Plex, use one of these approaches:

```text
Specials\Show Name - S00E01 - Creditless Opening.mkv
```

or create Plex-compatible hardlinks while keeping the original anime filenames unchanged.


---

### Plex cannot connect to the provider

Check:

```text
http://127.0.0.1:4567/health
```

Then run:

```text
TEST_PROVIDER.bat
```

If the provider is unavailable, check:

```text
logs\provider.log
```

Also verify that another application is not already using port `4567`.

---

### Metadata or artwork does not update after changing settings

Settings are loaded only when the provider starts, and Plex may continue using cached metadata or artwork even after the provider has changed what it returns.

After editing `settings.json`:

1. Save the file.
2. Stop the provider.
3. Start the provider again.
4. Refresh the series metadata in Plex.
5. Fully close and reopen Plex Web or the Plex app when testing cached artwork.

If the old metadata or artwork is still present, Plex may not fully replace previously selected images during a normal metadata refresh.

To force a complete metadata reset for that series:

1. Open the series in Plex.
2. Select **Unmatch**.
3. Match the series again using your MAL metadata agent.
4. Allow Plex to download the metadata and artwork again.

> [!IMPORTANT]
> Plex does not currently provide a way to delete individual cached artwork images from the series artwork picker. Unmatching and matching the series again is the reliable way to reset all metadata and artwork for that series.

For Square Art, also confirm that this setting is enabled:

```json
"poster_as_square_art": true
```

---

### Episode synopsis or score does not appear

Confirm these settings are enabled:

```json
"include_episode_synopses": true,
"include_episode_scores": true
```

Then restart the provider and refresh the series metadata in Plex. Existing cached episode metadata may require unmatching and matching the series again.

---

### The provider does not start after a server restart

Run `REGISTER_STARTUP.bat` as administrator.

Open Windows Task Scheduler and confirm that this task exists:

```text
MAL Plex Metadata Provider
```

If the Last Run Result is:

```text
0x41301
```

the task is currently running.

---

### Plex displays unrelated shows under Related Shows

Plex may generate its own Related Shows row using shared library metadata such as genres, cast, studio, or year.

The provider does not currently control all of Plex’s recommendation behaviour.

A show appearing in that row does not necessarily mean that MyAnimeList identifies it as a sequel, prequel, spin-off, or adaptation.

---

### Ratings appear on the series page but not on library cards

Plex handles custom-provider ratings differently from ratings supplied by Plex’s built-in metadata agents.

The MAL rating may still appear on series and episode detail pages, but Plex may not index custom-provider ratings for library sorting.

Changing `rating_source` between TMDB and IMDb changes the displayed audience-rating icon only; it does not fix sorting.

---

### Some cast or staff members are missing

Possible causes include:

- No Japanese voice actor is listed
- Voice-actor fallback is disabled
- MAL does not provide a compatible staff role
- The Tenrai endpoint did not return that person
- Plex ignored or cached part of the refreshed metadata

Check `logs\provider.log` while refreshing the series.

---


---

## Data sources and trademarks

Anime metadata is based on MyAnimeList-compatible data supplied through the Tenrai API.

This project is an independent community project and is not affiliated with, sponsored by, or endorsed by:

- MyAnimeList
- Plex
- Plex Media Server
- Tenrai
- Fribb

MyAnimeList, Plex, and other product names are trademarks of their respective owners.

Metadata, artwork, character images, and profile images remain the property of their respective owners and sources.

---

## Licence

This project is distributed under the MIT License.

See the [`LICENSE`](LICENSE) file for the complete licence text.

---

Copyright © 2026 PickledCakes
