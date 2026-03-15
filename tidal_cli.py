#!/usr/bin/env python3
"""Tidal CLI - Headless CLI for Tidal API, designed for LLM agent automation."""

import json
import logging
import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests.exceptions
import tidalapi
import typer

# T006: Log isolation
logging.getLogger("tidalapi").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# T003: App skeleton
app = typer.Typer(add_completion=False)
search_app = typer.Typer(help="Search the Tidal catalog.")
playlist_app = typer.Typer(help="Manage playlists.")
library_app = typer.Typer(help="Manage library favorites.")

app.add_typer(search_app, name="search")
app.add_typer(playlist_app, name="playlist")
app.add_typer(library_app, name="library")

state = {"json_output": False}
SESSION_FILE = Path(".tidal_session.json")


@app.callback()
def main(
    json_output: bool = typer.Option(False, "--json", help="Output as structured JSON."),
):
    """Tidal CLI - Headless CLI for LLM agent automation."""
    state["json_output"] = json_output


# T004: Output helper
def output(data, human_formatter):
    """Output data in JSON or human-readable text."""
    if state["json_output"]:
        typer.echo(json.dumps(data, ensure_ascii=False))
    else:
        typer.echo(human_formatter(data))


# T005: Session helpers
def save_session(session: tidalapi.Session):
    """Save session credentials to .tidal_session.json with mode 600."""
    data = {
        "token_type": session.token_type,
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expiry_time": session.expiry_time.isoformat() if session.expiry_time else None,
    }
    SESSION_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(SESSION_FILE, stat.S_IRUSR | stat.S_IWUSR)


def load_session() -> tidalapi.Session:
    """Load and validate session from file. Exits on error."""
    if not SESSION_FILE.exists():
        typer.echo(
            "Error: Not authenticated. The system administrator must first run "
            "'python tidal_cli.py auth' manually.",
            err=True,
        )
        raise typer.Exit(code=1)
    try:
        data = json.loads(SESSION_FILE.read_text())
        for field in ("token_type", "access_token", "refresh_token", "expiry_time"):
            if not data.get(field):
                raise ValueError(f"Missing or empty field: {field}")
        expiry_time = datetime.fromisoformat(data["expiry_time"])
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        typer.echo(
            f"Error: Invalid session file. Please re-run 'python tidal_cli.py auth'. ({e})",
            err=True,
        )
        raise typer.Exit(code=1)

    session = tidalapi.Session()
    session.load_oauth_session(
        data["token_type"], data["access_token"], data["refresh_token"], expiry_time
    )
    return session


# T007: Auth command (US1)
@app.command()
def auth():
    """Interactive OAuth authentication (human only)."""
    try:
        session = tidalapi.Session()
        login, future = session.login_oauth()
        url = login.verification_uri_complete
        if not url.startswith("http"):
            url = f"https://{url}"
        if state["json_output"]:
            typer.echo(f"Open this link in your browser to log in:\n{url}\n", err=True)
            typer.echo("Waiting for validation...", err=True)
        else:
            typer.echo(f"Open this link in your browser to log in:\n{url}\n")
            typer.echo("Waiting for validation...")
        future.result()
        save_session(session)
        output(
            {"status": "success", "message": "Authentication successful"},
            lambda d: "Authentication successful!",
        )
    except Exception:
        typer.echo(
            "Error: Authentication failed or expired. Please try again.", err=True
        )
        raise typer.Exit(code=1)


# T008: Search artist (US2)
@search_app.command("artist")
def search_artist(
    query: str = typer.Argument(..., help="Artist name to search for."),
):
    """Search for an artist by name in the Tidal catalog."""
    session = load_session()
    try:
        results = session.search(query, models=[tidalapi.artist.Artist], limit=20)
        artists = [{"id": a.id, "name": a.name} for a in results.get("artists", [])]

        def fmt(data):
            if not data:
                return ""
            return "\n".join(f"ID: {a['id']}  Name: {a['name']}" for a in data)

        output(artists, fmt)
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# T009: Search album (US2)
@search_app.command("album")
def search_album(
    query: str = typer.Argument(..., help="Album name to search for."),
):
    """Search for an album by name in the Tidal catalog."""
    session = load_session()
    try:
        results = session.search(query, models=[tidalapi.album.Album], limit=20)
        albums = []
        for a in results.get("albums", []):
            artist_name = a.artist.name if a.artist else "Unknown"
            year = getattr(a, "year", None)
            if year is None and getattr(a, "release_date", None):
                year = a.release_date.year
            albums.append(
                {"id": a.id, "name": a.name, "artist": artist_name, "year": year}
            )

        def fmt(data):
            if not data:
                return ""
            return "\n".join(
                f"ID: {a['id']}  Artist: {a['artist']}  Year: {a['year']}  Name: {a['name']}"
                for a in data
            )

        output(albums, fmt)
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# T010: Search track (US2)
@search_app.command("track")
def search_track(
    query: str = typer.Argument(..., help="Track name to search for."),
):
    """Search for a track by name in the Tidal catalog."""
    session = load_session()
    try:
        results = session.search(query, models=[tidalapi.media.Track], limit=20)
        tracks = [
            {
                "id": t.id,
                "name": t.name,
                "artist": t.artist.name if t.artist else "Unknown",
            }
            for t in results.get("tracks", [])
        ]

        def fmt(data):
            if not data:
                return ""
            return "\n".join(
                f"ID: {t['id']}  Artist: {t['artist']}  Name: {t['name']}"
                for t in data
            )

        output(tracks, fmt)
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# T011: Playlist list (US3)
@playlist_app.command("list")
def playlist_list():
    """List playlists created by the user."""
    session = load_session()
    try:
        playlists = session.user.playlists()
        data = [
            {"id": str(p.id), "name": p.name, "num_tracks": p.num_tracks}
            for p in playlists
        ]

        def fmt(data):
            if not data:
                return ""
            return "\n".join(
                f"ID: {p['id']}  Name: {p['name']} ({p['num_tracks']} tracks)"
                for p in data
            )

        output(data, fmt)
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# T012: Playlist create (US3)
@playlist_app.command("create")
def playlist_create(
    name: str = typer.Option(..., "--name", help="Playlist name."),
    desc: Optional[str] = typer.Option(None, "--desc", help="Playlist description."),
):
    """Create a new playlist."""
    if not name.strip():
        typer.echo("Error: Playlist name cannot be empty.", err=True)
        raise typer.Exit(code=1)
    session = load_session()
    try:
        new_playlist = session.user.create_playlist(name, desc or "")
        data = {
            "id": str(new_playlist.id),
            "name": name,
            "description": desc,
        }
        output(data, lambda d: f"Created playlist: ID: {d['id']}")
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# T013: Playlist rename (US3)
@playlist_app.command("rename")
def playlist_rename(
    playlist_id: str = typer.Option(..., "--playlist-id", help="Playlist ID to rename."),
    name: str = typer.Option(..., "--name", help="New playlist name."),
):
    """Rename an existing playlist."""
    session = load_session()
    try:
        playlist = session.playlist(playlist_id)
        old_name = playlist.name
        playlist.edit(title=name)
        data = {
            "status": "success",
            "id": str(playlist_id),
            "old_name": old_name,
            "new_name": name,
        }
        output(data, lambda d: f'Renamed playlist "{d["old_name"]}" to "{d["new_name"]}".')
    except requests.exceptions.HTTPError:
        typer.echo(f"Error: Playlist not found (ID: {playlist_id}).", err=True)
        raise typer.Exit(code=1)
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


# T014: Playlist delete (US3)
@playlist_app.command("delete")
def playlist_delete(
    playlist_id: str = typer.Option(..., "--playlist-id", help="Playlist ID to delete."),
):
    """Delete an existing playlist."""
    session = load_session()
    try:
        playlist = session.playlist(playlist_id)
        playlist_name = playlist.name
        playlist.delete()
        data = {
            "status": "success",
            "id": str(playlist_id),
            "name": playlist_name,
        }
        output(data, lambda d: f'Deleted playlist "{d["name"]}".')
    except requests.exceptions.HTTPError:
        typer.echo(f"Error: Playlist not found (ID: {playlist_id}).", err=True)
        raise typer.Exit(code=1)
    except requests.exceptions.ConnectionError:
        typer.echo(
            "Error: Unable to connect to Tidal. Check your network connection.",
            err=True,
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
