# Tasks: Tidal CLI Wrapper

**Input**: Design documents from `/specs/001-tidal-cli-wrapper/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/cli-commands.md

**Tests**: Not explicitly requested in the specification. Test tasks are excluded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All implementation is in a single file (`tidal_cli.py`) per FR-014.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (logically independent commands, no cross-dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency declaration

- [x] T001 Create requirements.txt with tidalapi and typer dependencies
- [x] T002 Update .gitignore to include .tidal_session.json and Python artifacts (__pycache__, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented. All tasks build the skeleton of `tidal_cli.py`.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Create tidal_cli.py with Typer app skeleton: main app with `@app.callback()` for global `--json` flag, `state` dict, and three subcommand groups (`search_app`, `playlist_app`, `library_app`) registered via `app.add_typer()`
- [x] T004 Implement `output()` helper function in tidal_cli.py: accepts data (dict or list) and a human_formatter callable, outputs JSON (`json.dumps`) or formatted text based on `state["json_output"]`
- [x] T005 Implement session helpers in tidal_cli.py: `save_session(session)` writes token_type, access_token, refresh_token, expiry_time (ISO 8601) to `.tidal_session.json` with mode 600; `load_session()` reads and validates the file, calls `session.load_oauth_session()`, returns a `tidalapi.Session` or exits with error
- [x] T006 Add log isolation in tidal_cli.py: set `logging.getLogger("tidalapi").setLevel(logging.CRITICAL)` and same for `httpx`/`requests` loggers to prevent parasitic output on stdout/stderr

**Checkpoint**: Foundation ready - `tidal_cli.py` has app structure, output helper, session management, and clean log isolation. User story implementation can now begin.

---

## Phase 3: User Story 1 - Initial Authentication by Human (Priority: P1) MVP

**Goal**: A human can run `auth` to link their Tidal account via Device Code Flow. The session is saved persistently and securely.

**Independent Test**: Run `python tidal_cli.py auth`, verify URL is displayed, complete browser flow, check `.tidal_session.json` exists with mode 600.

### Implementation for User Story 1

- [x] T007 [US1] Implement `auth` command in tidal_cli.py: call `session.login_oauth()`, display `verification_uri_complete` on stdout, block on `future.result()`, call `save_session()`, display success message. Handle errors (timeout, network) with stderr message and exit code 1. Support both text and JSON output per contracts/cli-commands.md.

**Checkpoint**: Authentication works end-to-end. A human can authenticate and the session file is created with restricted permissions. This is the MVP.

---

## Phase 4: User Story 2 - Music Search by LLM Agent (Priority: P1)

**Goal**: An LLM agent can search for artists, albums and tracks in the Tidal catalog and receive structured results with IDs and names.

**Independent Test**: Run `python tidal_cli.py search artist "Daft Punk"` and verify results contain ID and name. Same for album (with artist + year) and track search.

### Implementation for User Story 2

- [x] T008 [P] [US2] Implement `search artist` command in tidal_cli.py: call `session.search(query, models=[Artist], limit=20)`, format results with id and name per contracts/cli-commands.md (text and JSON modes), return empty list for no results (exit 0), handle errors with stderr and exit 1
- [x] T009 [P] [US2] Implement `search album` command in tidal_cli.py: call `session.search(query, models=[Album], limit=20)`, format results with id, name, artist_name (`album.artist.name`), release_year (`album.release_date.year`) per contracts/cli-commands.md, handle errors
- [x] T010 [P] [US2] Implement `search track` command in tidal_cli.py: call `session.search(query, models=[Track], limit=20)`, format results with id, name, artist_name (`track.artist.name`) per contracts/cli-commands.md, handle errors

**Checkpoint**: All three search commands work. An LLM agent can discover artists, albums and tracks by name.

---

## Phase 5: User Story 3 - Playlist Management by LLM Agent (Priority: P2)

**Goal**: An LLM agent can list, create, rename and delete the user's playlists.

**Independent Test**: List playlists, create one, rename it, then delete it. Verify each step returns expected output.

### Implementation for User Story 3

- [x] T011 [P] [US3] Implement `playlist list` command in tidal_cli.py: call `session.user.playlists()`, format results with id, name, num_tracks per contracts/cli-commands.md, return empty list if none (exit 0)
- [x] T012 [P] [US3] Implement `playlist create` command in tidal_cli.py: accept `--name` (required) and `--desc` (optional), call `session.user.create_playlist(name, description)`, return playlist id per contracts/cli-commands.md, validate name is not empty
- [x] T013 [P] [US3] Implement `playlist rename` command in tidal_cli.py: accept `--playlist-id` and `--name`, fetch playlist, call `playlist.edit(title=name)`, display old and new name per contracts/cli-commands.md, handle invalid playlist ID
- [x] T014 [P] [US3] Implement `playlist delete` command in tidal_cli.py: accept `--playlist-id`, fetch playlist, call `playlist.delete()`, display confirmation per contracts/cli-commands.md, handle invalid playlist ID

**Checkpoint**: Full playlist CRUD works. An LLM agent can manage playlists autonomously.

---

## Phase 6: User Story 4 - Playlist Content Manipulation by LLM Agent (Priority: P2)

**Goal**: An LLM agent can populate and modify playlist content: add albums, add individual tracks, remove tracks.

**Independent Test**: Create a playlist, add an album to it, add a track, remove a track. Verify confirmation messages at each step.

### Implementation for User Story 4

- [x] T015 [P] [US4] Implement `playlist add-album` command in tidal_cli.py: accept `--playlist-id` and `--album-id`, fetch album, get tracks via `album.tracks()`, extract IDs, call `playlist.add([track_ids])`, display count and names per contracts/cli-commands.md, handle invalid IDs
- [x] T016 [P] [US4] Implement `playlist add-track` command in tidal_cli.py: accept `--playlist-id` and `--track-id`, fetch track, call `playlist.add([track_id])`, display confirmation per contracts/cli-commands.md, handle invalid IDs
- [x] T017 [P] [US4] Implement `playlist remove-track` command in tidal_cli.py: accept `--playlist-id` and `--track-id`, fetch playlist tracks, find track index, call `playlist.remove_by_index(index)`, display confirmation per contracts/cli-commands.md, handle track not found in playlist

**Checkpoint**: Complete playlist content workflow works. The full agent workflow (search -> create playlist -> populate) is now functional.

---

## Phase 7: User Story 5 - Automatic Session Refresh (Priority: P3)

**Goal**: Expired tokens are refreshed transparently before command execution. The LLM agent is unaware of the refresh process.

**Independent Test**: Manually set `expiry_time` to a past date in `.tidal_session.json`, run any command, verify it succeeds and the session file is updated with a new expiry time.

### Implementation for User Story 5

- [x] T018 [US5] Enhance `load_session()` in tidal_cli.py: after `session.load_oauth_session()`, call `session.check_login()`. If True, call `save_session()` to persist any refreshed tokens. If False (refresh token expired), display error requesting re-authentication via stderr and exit 1.

**Checkpoint**: Session refresh is fully transparent. Commands work seamlessly even with expired access tokens.

---

## Phase 8: User Story 6 - User Library Management by LLM Agent (Priority: P3)

**Goal**: An LLM agent can add or remove artists, albums and tracks from the user's library (favorites).

**Independent Test**: Add an artist to the library, verify confirmation. Remove it, verify confirmation. Repeat for album and track.

### Implementation for User Story 6

- [x] T019 [P] [US6] Implement `library add` command in tidal_cli.py: accept mutually exclusive `--artist-id`, `--album-id`, `--track-id` (exactly one required), call `session.user.favorites.add_artist/add_album/add_track()`, fetch item name for confirmation, display per contracts/cli-commands.md, validate exactly one param provided, handle invalid IDs
- [x] T020 [P] [US6] Implement `library remove` command in tidal_cli.py: accept mutually exclusive `--artist-id`, `--album-id`, `--track-id` (exactly one required), call `session.user.favorites.remove_artist/remove_album/remove_track()`, fetch item name for confirmation, display per contracts/cli-commands.md, validate exactly one param provided, handle invalid IDs

**Checkpoint**: Library management works. All 6 user stories are now functional.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and quality assurance

- [x] T021 Verify exit codes (0/1), stderr/stdout separation, and log isolation across all commands in tidal_cli.py
- [x] T022 Validate complete workflow per quickstart.md scenarios: auth -> search artist -> search album -> create playlist -> add album -> add track -> rename -> remove track -> delete playlist -> library add/remove

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 Auth (Phase 3)**: Depends on Foundational - MVP milestone
- **US2 Search (Phase 4)**: Depends on Foundational - can run in parallel with US1
- **US3 Playlist Mgmt (Phase 5)**: Depends on Foundational - can run in parallel with US1/US2
- **US4 Playlist Content (Phase 6)**: Depends on Foundational - logically depends on US3 (needs playlists to exist)
- **US5 Session Refresh (Phase 7)**: Depends on Foundational (enhances load_session from T005)
- **US6 Library (Phase 8)**: Depends on Foundational - can run in parallel with all other stories
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: After Foundational - no dependencies on other stories
- **US2 (P1)**: After Foundational - no dependencies on other stories
- **US3 (P2)**: After Foundational - no dependencies on other stories
- **US4 (P2)**: After Foundational - logically uses playlists from US3 but code is independent
- **US5 (P3)**: After Foundational - enhances session helper from Phase 2
- **US6 (P3)**: After Foundational - no dependencies on other stories

### Within Each User Story

- Each command includes its own error handling (try/except HTTPError, ConnectionError)
- Each command supports both text and JSON output via the shared `output()` helper
- Commands are independent Typer functions that share only the session and output infrastructure

### Parallel Opportunities

- **T001 + T002**: Setup tasks can run in parallel
- **T003 + T006**: App skeleton and log isolation are independent
- **T008 + T009 + T010**: All search commands are independent
- **T011 + T012 + T013 + T014**: All playlist management commands are independent
- **T015 + T016 + T017**: All playlist content commands are independent
- **T019 + T020**: Library add and remove are independent
- **US1 + US2 + US3 + US6**: These stories can be implemented in any order after Foundational

---

## Parallel Example: User Story 2

```bash
# Launch all search commands together:
Task: "Implement search artist command in tidal_cli.py"
Task: "Implement search album command in tidal_cli.py"
Task: "Implement search track command in tidal_cli.py"
```

## Parallel Example: User Story 3

```bash
# Launch all playlist management commands together:
Task: "Implement playlist list command in tidal_cli.py"
Task: "Implement playlist create command in tidal_cli.py"
Task: "Implement playlist rename command in tidal_cli.py"
Task: "Implement playlist delete command in tidal_cli.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 Authentication
4. Complete Phase 4: US2 Search
5. **STOP and VALIDATE**: Auth + Search work end-to-end
6. An LLM agent can already authenticate and search the catalog

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 (Auth) -> Human can authenticate -> MVP milestone
3. Add US2 (Search) -> Agent can search catalog -> Deploy/Demo
4. Add US3 (Playlist Mgmt) -> Agent can manage playlists
5. Add US4 (Playlist Content) -> Full workflow complete -> Deploy/Demo
6. Add US5 (Session Refresh) -> Transparent token refresh
7. Add US6 (Library) -> Library favorites management -> Final release
8. Polish -> Validated and production-ready

---

## Notes

- All code resides in a single file `tidal_cli.py` per FR-014
- [P] tasks = logically independent commands, no cross-dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Error handling pattern: try/except with HTTPError + ConnectionError, stderr via typer.echo(err=True), exit via raise typer.Exit(code=1)
- Output pattern: each command calls output(data, formatter) which handles text/JSON switching
