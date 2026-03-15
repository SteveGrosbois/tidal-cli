# Research: Tidal CLI Wrapper

**Date**: 2026-03-15
**Feature**: 001-tidal-cli-wrapper

## Decision 1: OAuth Authentication Flow

**Decision**: Use the Device Code Flow via `session.login_oauth()`

**Rationale**: The Device Code Flow is best suited for a headless CLI. It returns a `LoginOAuth` object with `verification_uri_complete` (full URL with code), `verification_uri` (base URL), and `user_code`. The method returns a tuple `(login, future)` where `future.result()` blocks until the user validates in the browser.

**Alternatives considered**:
- `session.login_oauth_simple()`: Prints the URL and blocks automatically. Too simplistic, loses control over display and output formatting.
- `session.pkce_login_url()`: Requires a callback URL and redirect handling, unsuitable for a CLI without a local server.

## Decision 2: Session Persistence

**Decision**: Save to a JSON file (`.tidal_session.json`) the fields `token_type`, `access_token`, `refresh_token`, `expiry_time` (ISO 8601).

**Rationale**: The method `session.load_oauth_session(token_type, access_token, refresh_token, expiry_time)` allows restoring a session without re-authentication. JSON format is simple, readable and standard. File permissions (mode 600) secure the tokens.

**Alternatives considered**:
- SQLite: Oversized for 4 fields.
- Pickle: Not readable, security risk (deserialization).
- `.env` file: Less structured, no native date handling.

## Decision 3: Token Refresh

**Decision**: Call `session.check_login()` which automatically attempts a refresh if the token is expired. If it fails, return an error message requesting re-authentication.

**Rationale**: `check_login()` returns a boolean and handles refresh internally. If `False`, the refresh token itself is also expired. No need to manually handle `token_refresh()` except for advanced cases.

**Alternatives considered**:
- Manual `expiry_time` check + explicit call to `token_refresh()`: More control but more code, and `check_login()` already does this work.

## Decision 4: CLI Framework

**Decision**: Use Typer with subcommands via `app.add_typer()`.

**Rationale**: Typer allows creating subcommand groups (`search`, `playlist`, `library`) and top-level commands (`auth`) in a single file. The `@app.callback()` handles the global `--json` option. Type validation is automatic. `typer.echo(msg, err=True)` writes to stderr. `raise typer.Exit(code=1)` sets the exit code.

**Alternatives considered**:
- `argparse`: More verbose, no automatic type validation, less elegant subcommands.
- `click`: Typer is built on Click with a more modern API (type hints).
- `fire`: Less control over validation and documentation.

## Decision 5: Mixed Output Format

**Decision**: Human-readable text by default, JSON via global `--json`. Centralized via an `output()` helper function.

**Rationale**: The `--json` flag is defined in the `@app.callback()` of the root app and stored in a module-level dict `state = {"json_output": False}`. Each command calls `output(data, human_formatter)` which chooses the format.

**Alternatives considered**:
- JSON only: Less readable for human debugging.
- Text only: Fragile parsing for an LLM.
- Per-command option: Redundant, the global flag is cleaner.

## Decision 6: Log Isolation

**Decision**: Redirect `tidalapi` (and `requests`) logs to `/dev/null` or a null handler via `logging.getLogger("tidalapi").setLevel(logging.CRITICAL)`.

**Rationale**: `tidalapi` uses the standard `logging` module. By setting the level to CRITICAL, debug, info and warning messages are suppressed from stderr. Stdout remains clean for the LLM.

**Alternatives considered**:
- Redirect stderr entirely: Risk of masking our own error messages.
- File handler: Adds complexity for a headless tool.

## Decision 7: Search and Result Limit

**Decision**: Use `session.search(query, models=[...], limit=20)` with the `models` parameter to filter by type (Artist, Album, or Track). Limit set to 20 results.

**Rationale**: The `models` parameter of `session.search()` accepts `[tidalapi.artist.Artist]`, `[tidalapi.album.Album]`, or `[tidalapi.media.Track]` to filter results by type. A limit of 20 is a good compromise between completeness and readability for an LLM.

**Alternatives considered**:
- Limit of 10: Risk of missing relevant results.
- Limit of 50+: Too much data for an LLM context.
- Configurable limit: Overkill for the initial scope.

## Decision 8: Adding an Album to a Playlist

**Decision**: Retrieve tracks via `album.tracks()`, extract IDs, then call `playlist.add([track_ids])`.

**Rationale**: `tidalapi` has no direct method to add an entire album to a playlist. You must go through individual track IDs. The `playlist.add()` method accepts a list of track IDs.

**Alternatives considered**:
- No viable alternative: this is the only pattern supported by the API.

## Decision 9: Error Handling

**Decision**: Use a try/except pattern in each command with `requests.exceptions.HTTPError` and `requests.exceptions.ConnectionError` exceptions. Write errors to stderr via `typer.echo(msg, err=True)` and exit with `raise typer.Exit(code=1)`.

**Rationale**: `tidalapi` uses `requests` and raises `HTTPError` for API errors (401, 404, 429) and `ConnectionError` for network issues. These are the two main cases to handle.

**Alternatives considered**:
- Common decorator for try/except: Possible but adds complexity for a small number of commands.
- Custom exceptions: Oversized for a single-file script.
