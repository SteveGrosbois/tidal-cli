# Data Model: CLI Skills Directory

## Entities

### Skill File

A Claude Code skill is a Markdown file with YAML frontmatter stored at `skills/<name>/SKILL.md`.

| Field             | Type   | Required | Description                                      |
|-------------------|--------|----------|--------------------------------------------------|
| name              | string | yes      | Slash command name (e.g., `tidal-search`)        |
| description       | string | yes      | When to trigger the skill (for auto-invocation)  |
| allowed-tools     | string | no       | Comma-separated tools (e.g., `Bash, Read, Grep`) |
| argument-hint     | string | no       | Autocomplete hint (e.g., `"<query>"`)            |

**Body**: Markdown instructions for Claude describing:
- What the skill does
- Which CLI commands to run
- How to parse `--json` output
- How to handle errors

### Skill Inventory

| Skill Name      | Directory                        | CLI Commands Covered                                                                    |
|-----------------|----------------------------------|-----------------------------------------------------------------------------------------|
| tidal-auth      | `skills/tidal-auth/`     | `auth`                                                                                  |
| tidal-search    | `skills/tidal-search/`   | `search artist`, `search album`, `search track`                                        |
| tidal-playlist  | `skills/tidal-playlist/` | `playlist list`, `playlist create`, `playlist rename`, `playlist delete`, `playlist add-album`, `playlist add-track`, `playlist remove-track` |
| tidal-library   | `skills/tidal-library/`  | `library add`, `library remove`                                                         |

### CLI Command Reference

Each skill maps user intent to one of these commands:

| Command                  | Arguments                              | JSON Output Fields                |
|--------------------------|----------------------------------------|-----------------------------------|
| `tidal-cli auth`         | (none)                                 | (interactive, no JSON)            |
| `tidal-cli --json search artist <query>` | query (string)              | `[{id, name}]`                    |
| `tidal-cli --json search album <query>`  | query (string)              | `[{id, name, artist, year}]`      |
| `tidal-cli --json search track <query>`  | query (string)              | `[{id, name, artist}]`            |
| `tidal-cli --json playlist list`         | (none)                      | `[{id, name, num_tracks}]`        |
| `tidal-cli --json playlist create`       | --name, --desc (optional)   | `{id, name, description}`         |
| `tidal-cli --json playlist rename`       | --playlist-id, --name       | `{status, id, old_name, new_name}`|
| `tidal-cli --json playlist delete`       | --playlist-id               | `{status, id, name}`              |
| `tidal-cli --json playlist add-album`    | --playlist-id, --album-id   | `{status, tracks_added, album, playlist}` |
| `tidal-cli --json playlist add-track`    | --playlist-id, --track-id   | `{status, track, playlist}`       |
| `tidal-cli --json playlist remove-track` | --playlist-id, --track-id   | `{status, track, playlist}`       |
| `tidal-cli --json library add`           | --artist-id / --album-id / --track-id | `{status, type, id, name}` |
| `tidal-cli --json library remove`        | --artist-id / --album-id / --track-id | `{status, type, id, name}` |

### Error Messages

Skills must recognize and relay these CLI error patterns:

| Error Type           | CLI Message Pattern                                                       |
|----------------------|---------------------------------------------------------------------------|
| Not authenticated    | `"Error: Not authenticated. The system administrator must first run..."` |
| Network error        | `"Error: Unable to connect to Tidal. Check your network connection."`    |
| Entity not found     | `"Error: Artist/Album/Track not found (ID: {id})."`                      |
| Playlist not found   | `"Error: Playlist not found (ID: {id})."`                                |
| Track not in playlist| `"Error: Track not found in playlist (ID: {id})."`                       |
| Empty playlist name  | `"Error: Playlist name cannot be empty."`                                |
| Wrong library params | `"Error: You must provide exactly one of --artist-id, --album-id or --track-id."` |
