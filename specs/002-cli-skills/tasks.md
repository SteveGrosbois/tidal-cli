# Tasks: CLI Skills Directory

**Input**: Design documents from `/specs/002-cli-skills/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Create the skills directory structure

- [ ] T001 Create skill directories: `skills/tidal-auth/`, `skills/tidal-search/`, `skills/tidal-playlist/`, `skills/tidal-library/`

---

## Phase 2: User Story 4 - Authenticate via a skill (Priority: P1)

**Goal**: Enable users to launch the Tidal OAuth authentication process via `/tidal-auth`

**Independent Test**: Invoke `/tidal-auth` in Claude Code and verify the OAuth URL is displayed

### Implementation for User Story 4

- [ ] T002 [US4] Create authentication skill in `skills/tidal-auth/SKILL.md` with frontmatter (name: `tidal-auth`, description, allowed-tools: `Bash`) and instructions covering: running `tidal-cli auth`, displaying the OAuth login URL, handling already-authenticated state, error handling for network issues

**Checkpoint**: `/tidal-auth` should launch the OAuth process and guide the user through login

---

## Phase 3: User Story 1 - Search for music via a skill (Priority: P1) MVP

**Goal**: Enable users to search for artists, albums, and tracks via `/tidal-search`

**Independent Test**: Invoke `/tidal-search artist Daft Punk` and verify formatted results with ID and name

### Implementation for User Story 1

- [ ] T003 [US1] Create search skill in `skills/tidal-search/SKILL.md` with frontmatter (name: `tidal-search`, description, allowed-tools: `Bash, Read, Grep`, argument-hint: `"<artist|album|track> <query>"`) and instructions covering:
  - Parsing `$ARGUMENTS` to determine search type (artist, album, track) and query
  - Running `tidal-cli --json search artist|album|track "<query>"`
  - Formatting JSON output as a markdown table (artist: id/name, album: id/name/artist/year, track: id/name/artist)
  - Handling empty results with a clear message
  - Handling errors: not authenticated (redirect to `/tidal-auth`), network error, missing arguments

**Checkpoint**: `/tidal-search` should return formatted search results for all 3 types (artist, album, track)

---

## Phase 4: User Story 2 - Manage playlists via skills (Priority: P2)

**Goal**: Enable users to manage playlists (list, create, rename, delete, add/remove content) via `/tidal-playlist`

**Independent Test**: Invoke `/tidal-playlist list` and verify playlists display with ID, name, and track count

### Implementation for User Story 2

- [ ] T004 [US2] Create playlist skill in `skills/tidal-playlist/SKILL.md` with frontmatter (name: `tidal-playlist`, description, allowed-tools: `Bash, Read, Grep`, argument-hint: `"<list|create|rename|delete|add-album|add-track|remove-track> [options]"`) and instructions covering:
  - Parsing `$ARGUMENTS` to determine operation and parameters
  - Running the appropriate `tidal-cli --json playlist <subcommand>` with correct flags:
    - `playlist list` — format as table (id, name, num_tracks)
    - `playlist create --name "<name>" [--desc "<desc>"]` — display created playlist ID
    - `playlist rename --playlist-id <id> --name "<name>"` — confirm rename with old/new names
    - `playlist delete --playlist-id <id>` — confirm deletion with playlist name
    - `playlist add-album --playlist-id <id> --album-id <id>` — confirm with tracks_added count
    - `playlist add-track --playlist-id <id> --track-id <id>` — confirm with track and playlist names
    - `playlist remove-track --playlist-id <id> --track-id <id>` — confirm removal
  - Handling errors: not authenticated, playlist not found, track not found, track not in playlist, empty playlist name, network error
  - Guiding user with usage hints when arguments are missing or incomplete

**Checkpoint**: `/tidal-playlist` should handle all 7 playlist operations with formatted output

---

## Phase 5: User Story 3 - Manage favorites via skills (Priority: P3)

**Goal**: Enable users to add/remove artists, albums, and tracks from their Tidal library via `/tidal-library`

**Independent Test**: Invoke `/tidal-library add --artist-id 7804` and verify confirmation message

### Implementation for User Story 3

- [ ] T005 [US3] Create library skill in `skills/tidal-library/SKILL.md` with frontmatter (name: `tidal-library`, description, allowed-tools: `Bash, Read, Grep`, argument-hint: `"<add|remove> <--artist-id|--album-id|--track-id> <id>"`) and instructions covering:
  - Parsing `$ARGUMENTS` to determine operation (add/remove) and item type/ID
  - Running `tidal-cli --json library add|remove --artist-id|--album-id|--track-id <id>`
  - Formatting confirmation message with item type, name, and action taken
  - Handling errors: not authenticated, entity not found, wrong parameters (must provide exactly one ID type), network error

**Checkpoint**: `/tidal-library` should add/remove items from favorites with clear confirmation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Ensure consistency and discoverability across all skills

- [ ] T006 Review all 4 SKILL.md files for consistent formatting, error handling patterns, and frontmatter structure
- [ ] T007 Validate all 13 CLI commands are covered across the 4 skills (cross-reference with data-model.md command table)
- [ ] T008 Run quickstart.md validation checklist against delivered skills

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Stories (Phase 2–5)**: All depend on Phase 1 (directory creation)
  - No foundational phase needed — skills are independent Markdown files
  - User stories can proceed in parallel after setup
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 4 — Auth (P1)**: Can start after Setup — no dependencies on other stories
- **User Story 1 — Search (P1)**: Can start after Setup — references `/tidal-auth` in error handling but does not depend on its implementation
- **User Story 2 — Playlist (P2)**: Can start after Setup — independent of other stories
- **User Story 3 — Library (P3)**: Can start after Setup — independent of other stories

### Parallel Opportunities

After Phase 1 (Setup), all 4 skill files can be created in parallel since they are independent files with no shared dependencies:

```
T002 [US4] tidal-auth/SKILL.md    ─┐
T003 [US1] tidal-search/SKILL.md  ─┤ All parallel after T001
T004 [US2] tidal-playlist/SKILL.md─┤
T005 [US3] tidal-library/SKILL.md ─┘
```

---

## Implementation Strategy

### MVP First (User Story 4 + User Story 1)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Auth skill (T002)
3. Complete Phase 3: Search skill (T003)
4. **STOP and VALIDATE**: Test `/tidal-auth` and `/tidal-search` independently
5. User can authenticate and search — core value delivered

### Incremental Delivery

1. Setup → Auth + Search → MVP delivered
2. Add Playlist skill → Test `/tidal-playlist` → 11/13 commands covered
3. Add Library skill → Test `/tidal-library` → 13/13 commands covered
4. Polish → Consistency validated

### Parallel Strategy

1. Complete Setup (T001)
2. Create all 4 SKILL.md files in parallel (T002–T005)
3. Polish (T006–T008)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each skill file is created
- Stop at any checkpoint to validate story independently
