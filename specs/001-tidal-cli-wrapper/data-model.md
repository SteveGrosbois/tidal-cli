# Data Model: Tidal CLI Wrapper

**Date**: 2026-03-15
**Feature**: 001-tidal-cli-wrapper

## Entities

### Session (persisted locally)

Represents the user's authenticated connection to Tidal.

| Field          | Type     | Description                           | Constraints               |
|----------------|----------|---------------------------------------|---------------------------|
| token_type     | string   | Token type (e.g., "Bearer")           | Required                  |
| access_token   | string   | OAuth access token                    | Required, sensitive       |
| refresh_token  | string   | OAuth refresh token                   | Required, sensitive       |
| expiry_time    | datetime | Token expiration date/time (UTC)      | Required, ISO 8601 format |

**Persistence**: JSON file `.tidal_session.json` with permissions 600.
**Lifecycle**: Created by `auth` -> Read/refreshed by any other command -> Rewritten if refreshed -> Manually deleted by user.

**Validation**:
- All 4 fields must be present and non-empty.
- `expiry_time` must be a valid datetime.
- If the file is missing or invalid, any command (except `auth`) returns an error.

### Artist (read-only from Tidal API)

| Field | Type   | Description                   |
|-------|--------|-------------------------------|
| id    | int    | Tidal unique identifier       |
| name  | string | Artist or group name          |

**Source**: Returned by `session.search(query, models=[Artist])`.
**Uniqueness**: `id` is unique in the Tidal catalog.

### Album (read-only from Tidal API)

| Field        | Type   | Description                   |
|--------------|--------|-------------------------------|
| id           | int    | Tidal unique identifier       |
| name         | string | Album title                   |
| artist_name  | string | Associated artist name        |
| release_year | int    | Release year                  |

**Source**: Returned by `session.search(query, models=[Album])`. The `artist_name` field comes from `album.artist.name`. The `release_year` field comes from `album.release_date.year`.
**Uniqueness**: `id` is unique in the Tidal catalog.
**Relationship**: An Album contains N Tracks (accessible via `album.tracks()`).

### Playlist (read/write via Tidal API)

| Field       | Type            | Description                  |
|-------------|-----------------|------------------------------|
| id          | string (UUID)   | Unique playlist identifier   |
| name        | string          | Playlist name                |
| description | string or null  | Optional description         |
| num_tracks  | int             | Number of tracks             |

**Source**: `session.user.playlists()` for reading, `session.user.create_playlist()` for creation.
**Uniqueness**: `id` is unique.
**Lifecycle**: Created by `playlist create` -> Populated by `playlist add-album` / `playlist add-track` -> Modified by `playlist rename` / `playlist remove-track` -> Deletable by `playlist delete`.

**Validation**:
- `name` must not be empty when creating or renaming.

### Track (exposed via search and playlist operations)

| Field       | Type   | Description              |
|-------------|--------|--------------------------|
| id          | int    | Tidal unique identifier  |
| name        | string | Track title              |
| artist_name | string | Artist name              |

**Source**: Returned by `session.search(query, models=[Track])` or `album.tracks()`. The `artist_name` field comes from `track.artist.name`.
**Usage**: The agent can search for tracks via `search track`, then add them individually to a playlist via `playlist add-track --track-id <id>`. Track IDs can also be extracted from an album.

### Library / Favorites (read/write via Tidal API)

Represents the user's personal collection. Not a standalone entity, but a container for references to artists, albums and tracks.

**Source**: `session.user.favorites` exposes `add_artist()`, `remove_artist()`, `add_album()`, `remove_album()`, `add_track()`, `remove_track()` methods.

## Relationships

```
Session --[authenticates]--> User
User --[owns]--> Playlist*
User --[owns]--> Library
Library --[contains]--> Artist*
Library --[contains]--> Album*
Library --[contains]--> Track*
Playlist --[contains]--> Track*
Album --[contains]--> Track*
Artist --[created]--> Album*
```

## Output Format

### Text mode (default)

```
# search artist "Daft Punk"
ID: 7804  Name: Daft Punk
ID: 12345 Name: Daft Punk (Tribute)

# search album "Discovery"
ID: 1234  Artist: Daft Punk  Year: 2001  Name: Discovery
ID: 5678  Artist: Various    Year: 2003  Name: Discovery (Soundtrack)

# search track "Around the World"
ID: 56789  Artist: Daft Punk  Name: Around the World
ID: 99887  Artist: Red Hot Chili Peppers  Name: Around the World

# playlist list
ID: abc-123  Name: AI Mix (3 tracks)
ID: def-456  Name: Jazz Collection (15 tracks)

# playlist create --name "Test" --desc "Description"
Created playlist: ID: ghi-789

# playlist add-album --playlist-id abc-123 --album-id 1234
Added 14 tracks from album "Discovery" to playlist "AI Mix".

# playlist add-track --playlist-id abc-123 --track-id 56789
Added track "Around the World" to playlist "AI Mix".
```

### JSON mode (`--json`)

```json
// search artist "Daft Punk"
[
  {"id": 7804, "name": "Daft Punk"},
  {"id": 12345, "name": "Daft Punk (Tribute)"}
]

// search album "Discovery"
[
  {"id": 1234, "name": "Discovery", "artist": "Daft Punk", "year": 2001},
  {"id": 5678, "name": "Discovery (Soundtrack)", "artist": "Various", "year": 2003}
]

// search track "Around the World"
[
  {"id": 56789, "name": "Around the World", "artist": "Daft Punk"},
  {"id": 99887, "name": "Around the World", "artist": "Red Hot Chili Peppers"}
]

// playlist list
[
  {"id": "abc-123", "name": "AI Mix", "num_tracks": 3},
  {"id": "def-456", "name": "Jazz Collection", "num_tracks": 15}
]

// playlist create --name "Test" --desc "Description"
{"id": "ghi-789", "name": "Test", "description": "Description"}

// playlist add-album --playlist-id abc-123 --album-id 1234
{"status": "success", "tracks_added": 14, "album": "Discovery", "playlist": "AI Mix"}

// playlist add-track --playlist-id abc-123 --track-id 56789
{"status": "success", "track": "Around the World", "playlist": "AI Mix"}
```
