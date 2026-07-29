from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests
from flask import Flask, jsonify, request
from waitress import serve

PROVIDER_ID = "tv.plex.agents.custom.pickledcakes.myanimelist.tv"
PROVIDER_TITLE = "MyAnimeList via Tenrai (PoC)"
VERSION = "1.7.1"
ROOT_PATH = "/tv"


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_json_file(name: str, defaults: dict[str, Any]) -> dict[str, Any]:
    path = app_dir() / name
    values = defaults.copy()
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("root value must be a JSON object")
            values.update(loaded)
        except Exception as exc:
            print(f"WARNING: Could not read {name}: {exc}")
    return values


def bool_setting(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered in {"true", "yes", "on", "1"}:
            return True
        if lowered in {"false", "no", "off", "0"}:
            return False
    return default


CONFIG = load_json_file("config.json", {
    "port": 4567,
    "api_base": "https://api.tenrai.org/v1",
    "request_timeout_seconds": 20,
})
SETTINGS = load_json_file("settings.json", {
    "title_language": "default",
    "voice_actor_language": "Japanese",
    "voice_actor_fallback": True,
    "cast_image": "character",
    "include_cast": True,
    "include_directors": True,
    "include_writers": True,
    "include_producers": True,
    "include_genres": True,
    "include_themes": True,
    "include_demographics": True,
    "include_studios": True,
    "episode_title_language": "default",
    "include_episode_synopses": True,
    "episode_synopsis_fallback_requests": False,
    "include_episode_scores": True,
    "include_additional_posters": True,
    "poster_as_square_art": True,
    "include_background": False,
    "rating_source": "tmdb",
})

API_BASE = str(CONFIG.get("api_base", "https://api.tenrai.org/v1")).rstrip("/")
TIMEOUT = int(CONFIG.get("request_timeout_seconds", 20))
PORT = int(CONFIG.get("port", 4567))
PREFERRED_TITLE = str(SETTINGS.get("title_language", "default"))
PREFERRED_VOICE_LANGUAGE = str(SETTINGS.get("voice_actor_language", "Japanese"))
VOICE_ACTOR_FALLBACK = bool_setting(SETTINGS.get("voice_actor_fallback"), True)
CAST_IMAGE = str(SETTINGS.get("cast_image", "character"))
INCLUDE_CAST = bool_setting(SETTINGS.get("include_cast"), True)
INCLUDE_DIRECTORS = bool_setting(SETTINGS.get("include_directors"), True)
INCLUDE_WRITERS = bool_setting(SETTINGS.get("include_writers"), True)
INCLUDE_PRODUCERS = bool_setting(SETTINGS.get("include_producers"), True)
INCLUDE_GENRES = bool_setting(SETTINGS.get("include_genres"), True)
INCLUDE_THEMES = bool_setting(SETTINGS.get("include_themes"), True)
INCLUDE_DEMOGRAPHICS = bool_setting(SETTINGS.get("include_demographics"), True)
INCLUDE_STUDIOS = bool_setting(SETTINGS.get("include_studios"), True)
EPISODE_TITLE_LANGUAGE = str(SETTINGS.get("episode_title_language", "default")).strip().casefold()
INCLUDE_EPISODE_SYNOPSES = bool_setting(SETTINGS.get("include_episode_synopses"), True)
EPISODE_SYNOPSIS_FALLBACK_REQUESTS = bool_setting(
    SETTINGS.get("episode_synopsis_fallback_requests"), False
)
INCLUDE_EPISODE_SCORES = bool_setting(SETTINGS.get("include_episode_scores"), True)
INCLUDE_ADDITIONAL_PICTURES = bool_setting(SETTINGS.get("include_additional_posters"), True)
POSTER_AS_SQUARE_ART = bool_setting(SETTINGS.get("poster_as_square_art"), True)
INCLUDE_BACKGROUND = bool_setting(SETTINGS.get("include_background"), False)
RATING_SOURCE = str(SETTINGS.get("rating_source", "tmdb")).strip().casefold()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(app_dir() / "mal-provider.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("mal-provider")
app = Flask(__name__)
session = requests.Session()
session.headers.update({"User-Agent": f"MAL-Plex-Provider/{VERSION}"})
EPISODE_DETAIL_CACHE: dict[tuple[int, int], dict[str, Any]] = {}


class ProviderError(RuntimeError):
    pass


def api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    log.info("Tenrai GET %s params=%s", url, params)
    try:
        response = session.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ProviderError(f"Tenrai request failed: {exc}") from exc
    except ValueError as exc:
        raise ProviderError("Tenrai returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise ProviderError("Tenrai returned an unexpected response")
    return payload


def first_data(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ProviderError("Tenrai response did not contain a data object")
    return data


def data_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data", [])
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def parse_date(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)
    match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else None


def title_for(anime: dict[str, Any]) -> str:
    # Match the original bundle's configurable title preference.
    titles = anime.get("titles")
    wanted_order = [PREFERRED_TITLE, "Default", "English", "Japanese"]
    if isinstance(titles, list):
        seen: set[str] = set()
        for wanted in wanted_order:
            wanted_key = str(wanted).casefold()
            if wanted_key in seen:
                continue
            seen.add(wanted_key)
            for item in titles:
                if (
                    isinstance(item, dict)
                    and str(item.get("type") or "").casefold() == wanted_key
                    and item.get("title")
                ):
                    return str(item["title"])
    return str(anime.get("title") or anime.get("title_english") or anime.get("title_japanese") or "Unknown")


def original_japanese_title(anime: dict[str, Any]) -> str | None:
    value = anime.get("title_japanese")
    if value:
        return str(value)
    titles = anime.get("titles")
    if isinstance(titles, list):
        for item in titles:
            if (
                isinstance(item, dict)
                and str(item.get("type") or "").casefold() == "japanese"
                and item.get("title")
            ):
                return str(item["title"])
    return None


def episode_title_for(episode: dict[str, Any], number: int) -> str:
    language = EPISODE_TITLE_LANGUAGE
    field_orders = {
        "english": ("title", "title_english", "title_romanji", "title_japanese"),
        "japanese": ("title_japanese", "title", "title_romanji", "title_english"),
        "romanji": ("title_romanji", "title", "title_english", "title_japanese"),
        "romaji": ("title_romanji", "title", "title_english", "title_japanese"),
        "default": ("title", "title_english", "title_romanji", "title_japanese"),
    }
    for field in field_orders.get(language, field_orders["default"]):
        value = episode.get(field)
        if value:
            return str(value)
    return f"Episode {number}"


def rating_image() -> str:
    return "imdb://image.rating" if RATING_SOURCE == "imdb" else "themoviedb://image.rating"


def aired_date(anime: dict[str, Any]) -> str:
    aired = anime.get("aired")
    if isinstance(aired, dict):
        value = parse_date(aired.get("from"))
        if value:
            return value
    return f"{int(anime.get('year') or 1900):04d}-01-01"


def image_url(anime: dict[str, Any]) -> str | None:
    images = anime.get("images")
    if not isinstance(images, dict):
        return None
    jpg = images.get("jpg")
    if not isinstance(jpg, dict):
        return None
    return jpg.get("large_image_url") or jpg.get("image_url")


def duration_ms(anime: dict[str, Any]) -> int | None:
    duration = anime.get("duration")
    if not duration:
        return None
    match = re.search(r"(\d+)\s*min", str(duration), re.I)
    return int(match.group(1)) * 60_000 if match else None


def mal_id_from_text(*values: Any) -> int | None:
    for value in values:
        if value is None:
            continue
        text = str(value)
        for pattern in (
            r"\[mal-(\d+)\]",
            r"myanimelist(?:\.tv)?://(?:show/)?(?:mal-show-)?(\d+)",
            r"mal-show-(\d+)",
        ):
            m = re.search(pattern, text, re.I)
            if m:
                return int(m.group(1))
    return None


def show_key(mal_id: int) -> str:
    return f"mal-show-{mal_id}"


def season_key(mal_id: int, season: int = 1) -> str:
    return f"mal-season-{mal_id}-{season}"


def episode_key(mal_id: int, episode: int, season: int = 1) -> str:
    return f"mal-episode-{mal_id}-{season}-{episode}"


def guid_for(key: str) -> str:
    # Plex requires modern provider GUIDs to include the metadata type path,
    # e.g. provider://show/ratingKey, provider://season/ratingKey.
    if key.startswith("mal-show-"):
        kind = "show"
    elif key.startswith("mal-season-"):
        kind = "season"
    elif key.startswith("mal-episode-"):
        kind = "episode"
    else:
        raise ProviderError(f"Cannot determine GUID type for key: {key}")
    return f"{PROVIDER_ID}://{kind}/{key}"


def metadata_container(items: list[dict[str, Any]], offset: int = 0, total: int | None = None):
    return {
        "MediaContainer": {
            "offset": offset,
            "totalSize": len(items) if total is None else total,
            "identifier": PROVIDER_ID,
            "size": len(items),
            "Metadata": items,
        }
    }


def show_metadata(anime: dict[str, Any], include_children: bool = False, include_credits: bool = False) -> dict[str, Any]:
    mal_id = int(anime["mal_id"])
    title = title_for(anime)
    release = aired_date(anime)
    poster = image_url(anime)
    # Plex metadata providers call the square-art image type "backgroundSquare".
    # Reuse MAL's default poster and intentionally omit normal background art.
    square_art = poster if POSTER_AS_SQUARE_ART else None
    item: dict[str, Any] = {
        "ratingKey": show_key(mal_id),
        "key": f"/library/metadata/{show_key(mal_id)}",
        "guid": guid_for(show_key(mal_id)),
        "type": "show",
        "title": title,
        "originalTitle": original_japanese_title(anime),
        "originallyAvailableAt": release,
        "year": int(release[:4]),
        "summary": anime.get("synopsis") or "",
        "contentRating": anime.get("rating") or None,
        "studio": (", ".join(x.get("name") for x in anime.get("studios", []) if isinstance(x, dict) and x.get("name")) or None) if INCLUDE_STUDIOS else None,
        "duration": duration_ms(anime),
        "thumb": poster,
        "Image": (
            ([{"alt": title, "type": "coverPoster", "url": poster}] if poster else [])
            + ([{"alt": title, "type": "backgroundSquare", "url": square_art}] if square_art else [])
        ),
        "Genre": [
            {"tag": x["name"]}
            for group, enabled in (("genres", INCLUDE_GENRES), ("themes", INCLUDE_THEMES), ("demographics", INCLUDE_DEMOGRAPHICS))
            if enabled
            for x in anime.get(group, [])
            if isinstance(x, dict) and x.get("name")
        ],
        "Guid": [{"id": f"myanimelist://{mal_id}"}],
    }
    score = anime.get("score")
    if score is not None:
        item["Rating"] = [{"image": rating_image(), "type": "audience", "value": float(score)}]
    item = {k: v for k, v in item.items() if v is not None}
    if include_credits and (INCLUDE_CAST or INCLUDE_DIRECTORS or INCLUDE_WRITERS or INCLUDE_PRODUCERS):
        credits = get_show_credits(mal_id)
        enabled_fields = {
            "Role": INCLUDE_CAST,
            "Director": INCLUDE_DIRECTORS,
            "Writer": INCLUDE_WRITERS,
            "Producer": INCLUDE_PRODUCERS,
        }
        for field, enabled in enabled_fields.items():
            if enabled and credits.get(field):
                item[field] = credits[field]
    if include_children:
        season = season_metadata(anime, 1, include_children=False)
        item["Children"] = {"size": 1, "Metadata": [season]}
    return item


def season_metadata(anime: dict[str, Any], season: int = 1, include_children: bool = False) -> dict[str, Any]:
    mal_id = int(anime["mal_id"])
    title = title_for(anime)
    release = aired_date(anime)
    poster = image_url(anime)
    item: dict[str, Any] = {
        "ratingKey": season_key(mal_id, season),
        "key": f"/library/metadata/{season_key(mal_id, season)}",
        "guid": guid_for(season_key(mal_id, season)),
        "type": "season",
        "title": f"Season {season}",
        "index": season,
        "originallyAvailableAt": release,
        "year": int(release[:4]),
        "thumb": poster,
        "parentRatingKey": show_key(mal_id),
        "parentKey": f"/library/metadata/{show_key(mal_id)}",
        "parentGuid": guid_for(show_key(mal_id)),
        "parentType": "show",
        "parentTitle": title,
        "parentThumb": poster,
    }
    if include_children:
        episodes = get_all_episodes(mal_id)
        item["Children"] = {"size": len(episodes), "Metadata": [episode_metadata(anime, ep, fetch_synopsis=True) for ep in episodes]}
    return {k: v for k, v in item.items() if v is not None}


def get_episode_detail(mal_id: int, number: int) -> dict[str, Any]:
    """Fetch and cache one MAL episode record.

    Tenrai normally includes synopsis, score and multilingual titles in the
    paginated episode response. This endpoint is retained only as an optional
    compatibility fallback for incomplete records.
    """
    cache_key = (mal_id, number)
    if cache_key in EPISODE_DETAIL_CACHE:
        return EPISODE_DETAIL_CACHE[cache_key]

    try:
        detail = first_data(api_get(f"/anime/{mal_id}/episodes/{number}"))
    except ProviderError as exc:
        log.warning(
            "Optional episode synopsis request failed for MAL %s episode %s: %s",
            mal_id,
            number,
            exc,
        )
        detail = {}

    EPISODE_DETAIL_CACHE[cache_key] = detail
    return detail


def episode_metadata(
    anime: dict[str, Any],
    episode: dict[str, Any],
    season: int = 1,
    fetch_synopsis: bool = False,
) -> dict[str, Any]:
    mal_id = int(anime["mal_id"])
    number = int(episode.get("mal_id") or episode.get("episode") or 0)
    show_title = title_for(anime)
    date = parse_date(episode.get("aired")) or aired_date(anime)

    synopsis = episode.get("synopsis") or episode.get("summary") or ""
    if (
        INCLUDE_EPISODE_SYNOPSES
        and EPISODE_SYNOPSIS_FALLBACK_REQUESTS
        and fetch_synopsis
        and not synopsis
        and number > 0
    ):
        detail = get_episode_detail(mal_id, number)
        synopsis = detail.get("synopsis") or detail.get("summary") or ""
        # Individual episode records may contain a better title/date as well.
        if detail:
            episode = {**episode, **detail}
        detail_date = parse_date(detail.get("aired"))
        if detail_date:
            date = detail_date

    item = {
        "ratingKey": episode_key(mal_id, number, season),
        "key": f"/library/metadata/{episode_key(mal_id, number, season)}",
        "guid": guid_for(episode_key(mal_id, number, season)),
        "type": "episode",
        "title": episode_title_for(episode, number),
        "originalTitle": episode.get("title_japanese") or None,
        "summary": synopsis,
        "index": number,
        "originallyAvailableAt": date,
        "year": int(date[:4]),
        "parentRatingKey": season_key(mal_id, season),
        "parentKey": f"/library/metadata/{season_key(mal_id, season)}",
        "parentGuid": guid_for(season_key(mal_id, season)),
        "parentType": "season",
        "parentTitle": f"Season {season}",
        "grandparentRatingKey": show_key(mal_id),
        "grandparentKey": f"/library/metadata/{show_key(mal_id)}",
        "grandparentGuid": guid_for(show_key(mal_id)),
        "grandparentType": "show",
        "grandparentTitle": show_title,
    }
    raw_episode_score = episode.get("score")
    if INCLUDE_EPISODE_SCORES and raw_episode_score is not None:
        try:
            score_value = float(raw_episode_score)
            # MAL episode votes are presented on a five-point scale. Plex
            # audience ratings are sent on a ten-point scale for consistency.
            if 0.0 <= score_value <= 5.0:
                item["Rating"] = [{
                    "image": rating_image(),
                    "type": "audience",
                    "value": round(score_value * 2.0, 1),
                }]
            else:
                log.warning(
                    "Ignoring unexpected episode score scale for MAL %s episode %s: %s",
                    mal_id,
                    number,
                    raw_episode_score,
                )
        except (TypeError, ValueError):
            log.warning(
                "Ignoring invalid episode score for MAL %s episode %s: %r",
                mal_id,
                number,
                raw_episode_score,
            )

    return {k: v for k, v in item.items() if v is not None}


def get_anime(mal_id: int) -> dict[str, Any]:
    return first_data(api_get(f"/anime/{mal_id}"))


def search_anime(title: str) -> list[dict[str, Any]]:
    return data_list(api_get("/anime", {"q": title, "limit": 10}))


def get_all_episodes(mal_id: int, max_pages: int = 20) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        payload = api_get(f"/anime/{mal_id}/episodes", {"page": page})
        out.extend(data_list(payload))
        pagination = payload.get("pagination") or {}
        if not isinstance(pagination, dict) or not pagination.get("has_next_page"):
            break
    return out


def safe_data_list(path: str) -> list[dict[str, Any]]:
    try:
        return data_list(api_get(path))
    except ProviderError as exc:
        # Credits are optional. A temporary API problem should not prevent the
        # rest of the show's metadata from refreshing.
        log.warning("Optional credits request failed for %s: %s", path, exc)
        return []


def person_image_url(person: dict[str, Any]) -> str | None:
    images = person.get("images")
    if not isinstance(images, dict):
        return None
    jpg = images.get("jpg")
    if not isinstance(jpg, dict):
        return None
    return jpg.get("image_url") or jpg.get("large_image_url")


def character_image_url(character: dict[str, Any]) -> str | None:
    images = character.get("images")
    if not isinstance(images, dict):
        return None
    jpg = images.get("jpg")
    if not isinstance(jpg, dict):
        return None
    return jpg.get("image_url") or jpg.get("large_image_url")


def get_additional_picture_urls(mal_id: int) -> list[str]:
    if not INCLUDE_ADDITIONAL_PICTURES:
        return []
    urls: list[str] = []
    for entry in safe_data_list(f"/anime/{mal_id}/pictures"):
        images = entry.get("jpg") if isinstance(entry, dict) else None
        if not isinstance(images, dict):
            continue
        url = images.get("large_image_url") or images.get("image_url")
        if url and str(url) not in urls:
            urls.append(str(url))
    return urls


def unique_people(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        tag = str(item.get("tag") or "").strip()
        role = str(item.get("role") or "").strip()
        if not tag:
            continue
        key = (tag.casefold(), role.casefold())
        if key in seen:
            continue
        seen.add(key)
        result.append({k: v for k, v in item.items() if v})
    return result


def get_show_credits(mal_id: int) -> dict[str, list[dict[str, Any]]]:
    roles: list[dict[str, Any]] = []
    directors: list[dict[str, Any]] = []
    writers: list[dict[str, Any]] = []
    producers: list[dict[str, Any]] = []

    # MAL lists voice performers per character and language. Prefer exactly one
    # Japanese performer for each character. If none exists, use the first
    # performer MAL supplies as a fallback.
    for entry in safe_data_list(f"/anime/{mal_id}/characters"):
        character = entry.get("character")
        if not isinstance(character, dict):
            continue
        character_name = str(character.get("name") or "").strip()
        voice_actors = entry.get("voice_actors")
        if not isinstance(voice_actors, list) or not voice_actors:
            continue
        valid = [x for x in voice_actors if isinstance(x, dict) and isinstance(x.get("person"), dict)]
        if not valid:
            continue
        chosen = next(
            (x for x in valid if str(x.get("language") or "").casefold() == PREFERRED_VOICE_LANGUAGE.casefold()),
            None,
        )
        if chosen is None:
            if not VOICE_ACTOR_FALLBACK:
                continue
            chosen = valid[0]
        person = chosen["person"]
        actor_name = str(person.get("name") or "").strip()
        if not actor_name:
            continue
        role_item: dict[str, Any] = {"tag": actor_name, "role": character_name}
        # The original bundle defaults to character artwork for cast entries,
        # with an option to use the voice performer's photo instead.
        if CAST_IMAGE.casefold() == "voice actor".casefold():
            thumb = person_image_url(person)
        else:
            thumb = character_image_url(character)
        if thumb:
            role_item["thumb"] = thumb
        roles.append(role_item)

    # MAL's staff endpoint supplies people plus one or more production positions.
    for entry in safe_data_list(f"/anime/{mal_id}/staff"):
        person = entry.get("person")
        if not isinstance(person, dict):
            continue
        name = str(person.get("name") or "").strip()
        if not name:
            continue
        base: dict[str, Any] = {"tag": name}
        thumb = person_image_url(person)
        if thumb:
            base["thumb"] = thumb
        positions = entry.get("positions")
        if not isinstance(positions, list):
            continue
        normalized = [str(x).strip().casefold() for x in positions if x]
        if any("director" in x for x in normalized):
            directors.append(base.copy())
        if any(any(term in x for term in ("script", "screenplay", "series composition", "original creator")) for x in normalized):
            writers.append(base.copy())
        if any("producer" in x for x in normalized):
            producers.append(base.copy())

    return {
        "Role": unique_people(roles),
        "Director": unique_people(directors),
        "Writer": unique_people(writers),
        "Producer": unique_people(producers),
    }


def parse_key(key: str) -> tuple[str, int, int | None, int | None]:
    patterns = [
        ("show", r"^mal-show-(\d+)$"),
        ("season", r"^mal-season-(\d+)-(\d+)$"),
        ("episode", r"^mal-episode-(\d+)-(\d+)-(\d+)$"),
    ]
    for kind, pattern in patterns:
        m = re.match(pattern, key)
        if m:
            nums = [int(v) for v in m.groups()]
            return kind, nums[0], nums[1] if len(nums) > 1 else None, nums[2] if len(nums) > 2 else None
    raise ProviderError(f"Unknown rating key: {key}")


@app.before_request
def log_request() -> None:
    log.info("%s %s body=%s", request.method, request.full_path, request.get_json(silent=True))

@app.after_request
def log_response(response):
    log.info("%s %s -> %s", request.method, request.path, response.status_code)
    return response


@app.get("/health")
def health():
    return jsonify({"status": "ok", "provider": PROVIDER_TITLE, "api_base": API_BASE, "time": datetime.now(timezone.utc).isoformat()})


@app.get("/")
@app.get(ROOT_PATH)
def provider_info():
    types = [{"type": t, "Scheme": [{"scheme": PROVIDER_ID}]} for t in (2, 3, 4)]
    return jsonify({
        "MediaProvider": {
            "identifier": PROVIDER_ID,
            "title": PROVIDER_TITLE,
            "version": VERSION,
            "Types": types,
            "Feature": [
                {"type": "metadata", "key": "/library/metadata"},
                {"type": "match", "key": "/library/metadata/matches"},
            ],
        }
    })


@app.post("/library/metadata/matches")
@app.post("/tv/tv/library/metadata/matches")
@app.post(f"{ROOT_PATH}/library/metadata/matches")
def matches():
    body = request.get_json(force=True) or {}
    media_type = int(body.get("type", 0))
    include_children = bool(int(body.get("includeChildren", 0) or 0))
    explicit_id = mal_id_from_text(body.get("guid"), body.get("title"), body.get("parentTitle"), body.get("grandparentTitle"), body.get("filename"))

    if media_type == 2:
        if explicit_id:
            results = [get_anime(explicit_id)]
        else:
            title = str(body.get("title") or "").strip()
            if not title:
                return jsonify(metadata_container([]))
            results = search_anime(title)
        items = [show_metadata(x, include_children) for x in results[: (10 if body.get("manual") else 1)]]
        return jsonify(metadata_container(items))

    title = str(body.get("parentTitle") or body.get("grandparentTitle") or "").strip()
    if explicit_id:
        anime = get_anime(explicit_id)
    elif title:
        found = search_anime(title)
        if not found:
            return jsonify(metadata_container([]))
        anime = found[0]
    else:
        return jsonify(metadata_container([]))

    if media_type == 3:
        season = int(body.get("index") or 1)
        return jsonify(metadata_container([season_metadata(anime, season, include_children)]))
    if media_type == 4:
        season = int(body.get("parentIndex") or 1)
        number = int(body.get("index") or 0)
        episodes = get_all_episodes(int(anime["mal_id"]))
        episode = next((x for x in episodes if int(x.get("mal_id") or 0) == number), {"mal_id": number, "title": f"Episode {number}"})
        return jsonify(metadata_container([episode_metadata(anime, episode, season, fetch_synopsis=True)]))
    return jsonify(metadata_container([]))


@app.get("/library/metadata/<rating_key>")
@app.get("/tv/tv/library/metadata/<rating_key>")
@app.get(f"{ROOT_PATH}/library/metadata/<rating_key>")
def metadata(rating_key: str):
    try:
        kind, mal_id, season, episode = parse_key(rating_key)
        anime = get_anime(mal_id)
        include_children = request.args.get("includeChildren", "0") == "1"
        if kind == "show":
            item = show_metadata(anime, include_children, include_credits=True)
        elif kind == "season":
            item = season_metadata(anime, season or 1, include_children)
        else:
            eps = get_all_episodes(mal_id)
            ep = next((x for x in eps if int(x.get("mal_id") or 0) == int(episode or 0)), {"mal_id": episode or 0, "title": f"Episode {episode}"})
            item = episode_metadata(anime, ep, season or 1, fetch_synopsis=True)
        return jsonify(metadata_container([item]))
    except ProviderError as exc:
        log.exception("Metadata failed")
        return jsonify({"error": str(exc)}), 404


@app.get("/library/metadata/<rating_key>/children")
@app.get("/tv/tv/library/metadata/<rating_key>/children")
@app.get(f"{ROOT_PATH}/library/metadata/<rating_key>/children")
def children(rating_key: str):
    try:
        kind, mal_id, season, _ = parse_key(rating_key)
        anime = get_anime(mal_id)
        if kind == "show":
            items = [season_metadata(anime, 1, False)]
        elif kind == "season":
            items = [episode_metadata(anime, ep, season or 1, fetch_synopsis=True) for ep in get_all_episodes(mal_id)]
        else:
            items = []
        start = int(request.args.get("X-Plex-Container-Start", request.headers.get("X-Plex-Container-Start", 0)))
        size = int(request.args.get("X-Plex-Container-Size", request.headers.get("X-Plex-Container-Size", 20)))
        return jsonify(metadata_container(items[start:start + size], start, len(items)))
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), 404


@app.get("/library/metadata/<rating_key>/grandchildren")
@app.get("/tv/tv/library/metadata/<rating_key>/grandchildren")
@app.get(f"{ROOT_PATH}/library/metadata/<rating_key>/grandchildren")
def grandchildren(rating_key: str):
    try:
        kind, mal_id, _, _ = parse_key(rating_key)
        if kind != "show":
            return jsonify(metadata_container([]))
        anime = get_anime(mal_id)
        items = [episode_metadata(anime, ep, 1, fetch_synopsis=True) for ep in get_all_episodes(mal_id)]
        start = int(request.args.get("X-Plex-Container-Start", request.headers.get("X-Plex-Container-Start", 0)))
        size = int(request.args.get("X-Plex-Container-Size", request.headers.get("X-Plex-Container-Size", 20)))
        return jsonify(metadata_container(items[start:start + size], start, len(items)))
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), 404


@app.get("/library/metadata/<rating_key>/extras")
@app.get("/tv/tv/library/metadata/<rating_key>/extras")
@app.get(f"{ROOT_PATH}/library/metadata/<rating_key>/extras")
def extras(rating_key: str):
    # Plex currently probes this endpoint, but public custom-provider guidance
    # says remote extras are not yet officially supported. Return Tenrai trailer
    # candidates experimentally so future PMS versions can consume them without
    # another provider update.
    try:
        kind, mal_id, _, _ = parse_key(rating_key)
        if kind != "show":
            return jsonify(metadata_container([]))
        items = get_experimental_trailers(mal_id)
        log.info("Experimental extras for MAL %s: %d candidate(s)", mal_id, len(items))
        return jsonify(metadata_container(items))
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), 404


@app.get("/library/metadata/<rating_key>/images")
@app.get("/tv/tv/library/metadata/<rating_key>/images")
@app.get(f"{ROOT_PATH}/library/metadata/<rating_key>/images")
def images(rating_key: str):
    try:
        _, mal_id, _, _ = parse_key(rating_key)
        anime = get_anime(mal_id)
        poster = image_url(anime)
        title = title_for(anime)
        images_out: list[dict[str, Any]] = []
        seen_urls: set[tuple[str, str]] = set()

        def add_image(image_type: str, url: str | None, alt: str) -> None:
            if not url:
                return
            key = (image_type, str(url))
            if key in seen_urls:
                return
            seen_urls.add(key)
            images_out.append({"type": image_type, "url": str(url), "alt": alt})

        # Match the original bundle: default MAL poster plus every additional
        # MAL picture as selectable posters. Only the default poster is also
        # assigned as Plex Square Art. No normal background is supplied.
        add_image("coverPoster", poster, title)
        if POSTER_AS_SQUARE_ART:
            add_image("backgroundSquare", poster, title)
        for index, url in enumerate(get_additional_picture_urls(mal_id), start=1):
            add_image("coverPoster", url, f"{title} — MAL picture {index}")

        # The artwork picker expects Image directly under MediaContainer.
        # Provider image type "backgroundSquare" is serialized by PMS as squareArt.
        return jsonify({
            "MediaContainer": {
                "offset": 0,
                "totalSize": len(images_out),
                "identifier": PROVIDER_ID,
                "size": len(images_out),
                "Image": images_out,
            }
        })
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), 404


@app.errorhandler(Exception)
def unhandled(exc: Exception):
    log.exception("Unhandled error")
    return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    log.info("Starting %s v%s", PROVIDER_TITLE, VERSION)
    log.info("Provider URL for Plex: http://127.0.0.1:%d%s", PORT, ROOT_PATH)
    log.info("Health check: http://127.0.0.1:%d/health", PORT)
    log.info("Loaded user settings from: %s", app_dir() / "settings.json")
    log.info("Title: %s | Voice actors: %s | Fallback: %s | Cast image: %s", PREFERRED_TITLE, PREFERRED_VOICE_LANGUAGE, VOICE_ACTOR_FALLBACK, CAST_IMAGE)
    log.info("Cast=%s Directors=%s Writers=%s Producers=%s", INCLUDE_CAST, INCLUDE_DIRECTORS, INCLUDE_WRITERS, INCLUDE_PRODUCERS)
    log.info("Genres=%s Themes=%s Demographics=%s Studios=%s", INCLUDE_GENRES, INCLUDE_THEMES, INCLUDE_DEMOGRAPHICS, INCLUDE_STUDIOS)
    log.info("Episode titles=%s | Synopses=%s | Fallback requests=%s | Scores=%s", EPISODE_TITLE_LANGUAGE, INCLUDE_EPISODE_SYNOPSES, EPISODE_SYNOPSIS_FALLBACK_REQUESTS, INCLUDE_EPISODE_SCORES)
    log.info("Additional posters=%s", INCLUDE_ADDITIONAL_PICTURES)
    log.info("Square art from poster=%s | Background=%s | Rating badge=%s", POSTER_AS_SQUARE_ART, INCLUDE_BACKGROUND, RATING_SOURCE)
    serve(app, host="0.0.0.0", port=PORT, threads=8)
