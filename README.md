# MyAnimeList Plex Metadata Provider

A modern MyAnimeList metadata provider for Plex Media Server.

This provider uses MyAnimeList data through the Tenrai API and is designed as a replacement for the legacy `MyAnimeList.bundle` Plex plugin.

It supports modern Plex Custom Metadata Providers and can run automatically in the background when Windows starts.

> [!IMPORTANT]
> Plex Custom Metadata Providers are still an evolving feature. Some metadata fields may behave differently across Plex Web, iOS, Android, Apple TV, and other Plex clients.

---

## Features

- MyAnimeList anime search and matching
- Default, English, or Japanese series titles
- Anime synopsis
- MAL score displayed with a configurable rating badge
- Release date and year
- Content rating
- Episode titles and air dates
- Genres
- Themes
- Demographics
- Studios
- Additional MAL posters
- MAL poster used as Plex Square Art
- Optional cast and staff metadata
- Japanese voice actors preferred by default
- Fallback voice actor when no Japanese actor is available
- Character or voice-actor profile images
- Directors, writers, and producers where available
- User-editable `settings.json`
- One-click Windows installation
- Automatic startup using Windows Task Scheduler
- Standalone Windows EXE releases
- Provider logging and health checks

---

## Download

Download the latest Windows ZIP from the repository's **Releases** page.

Extract the ZIP to a permanent folder, for example:

```text
C:\MAL-Plex-Provider
