# Feature Specification: Tidal CLI - LLM Agent Wrapper

**Feature Branch**: `001-tidal-cli-wrapper`
**Created**: 2026-03-15
**Status**: Draft
**Input**: User description: "Headless CLI to interact with the Tidal API, designed for an LLM agent to search music, create playlists and populate them autonomously"

## Clarifications

### Session 2026-03-15

- Q: What output format for results (JSON, plain text, or mixed)? → A: Mixed mode - human-readable text by default, `--json` option to switch to structured JSON.
- Q: Should there be an optional artist filter on album search? → A: No. The artist name is displayed in results, the LLM agent disambiguates on its own.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Initial authentication by human (Priority: P1)

A human administrator runs the authentication command to link their Tidal account. The system displays a login URL in the terminal. The human clicks the link, authorizes the application in their browser, and the session is saved persistently and securely in a local file. This step is a prerequisite for all other functionality.

**Why this priority**: Without authentication, no other command can work. It is the foundation of the entire system.

**Independent Test**: Can be tested by running the authentication command, verifying the URL is displayed, completing the flow in a browser, then checking that the session file is created with appropriate permissions.

**Acceptance Scenarios**:

1. **Given** no existing session, **When** the administrator runs the authentication command, **Then** a login URL is displayed in the terminal and the system waits for browser validation.
2. **Given** the administrator has validated the login in their browser, **When** the authorization flow is completed, **Then** a session file is created locally with restricted permissions (read/write only by owner) and a success message is displayed.
3. **Given** an existing valid session, **When** the administrator re-runs the authentication command, **Then** the session is renewed and the session file is updated.

---

### User Story 2 - Music search by LLM agent (Priority: P1)

An LLM agent executes search commands to find artists, albums and tracks in the Tidal catalog. The system returns a structured list of results containing the name and unique identifier of each matching item. The agent can then precisely identify content to manipulate.

**Why this priority**: Search is the foundation of all music interaction. Without being able to identify artists, albums and tracks, the agent cannot populate playlists.

**Independent Test**: Can be tested by running an artist search with a known name (e.g., "Daft Punk") and verifying that results contain at least one item with a name and identifier. Same test for album and track search.

**Acceptance Scenarios**:

1. **Given** a valid authenticated session, **When** the agent searches for an artist by name, **Then** the system returns a list of results in human-readable text (by default) or JSON (if `--json` option is used) with the name and unique identifier of each matching artist, on stdout.
2. **Given** a valid authenticated session, **When** the agent searches for an album by name, **Then** the system returns a list of results with the album name, artist name, release year and unique identifier of each matching album.
3. **Given** a valid authenticated session, **When** the agent searches for a track by name, **Then** the system returns a list of results with the track name, artist name and unique identifier of each matching track.
4. **Given** a valid authenticated session, **When** the agent searches for an item that does not exist, **Then** the system returns an empty list without error and exit code 0.
5. **Given** no authenticated session, **When** the agent attempts a search, **Then** the system returns an explicit error message indicating authentication is required and a non-zero exit code.

---

### User Story 3 - Playlist management by LLM agent (Priority: P2)

An LLM agent can list, create, rename and delete the user's playlists. For each listed playlist, the name and identifier are displayed. When creating, the agent provides a name and optionally a description, and receives the identifier of the newly created playlist.

**Why this priority**: Playlist management is necessary to organize music, but only works after authentication and search. It is the foundation of the ultimate goal (populating playlists).

**Independent Test**: Can be tested by listing playlists, creating a playlist, renaming it, then deleting it.

**Acceptance Scenarios**:

1. **Given** a valid authenticated session, **When** the agent requests the playlist list, **Then** the system returns the user's playlists with their name and unique identifier.
2. **Given** a valid authenticated session, **When** the agent creates a playlist with a name, **Then** the system creates the playlist and returns its unique identifier.
3. **Given** a valid authenticated session, **When** the agent creates a playlist with a name and description, **Then** the system creates the playlist with the associated description and returns its unique identifier.
4. **Given** no existing playlists for the user, **When** the agent requests the playlist list, **Then** the system returns an empty list without error.
5. **Given** a valid authenticated session and an existing playlist, **When** the agent renames the playlist by providing its identifier and a new name, **Then** the playlist name is updated and a confirmation message is displayed.
6. **Given** a valid authenticated session and an existing playlist, **When** the agent deletes the playlist by providing its identifier, **Then** the playlist is deleted and a confirmation message is displayed.
7. **Given** a valid authenticated session, **When** the agent attempts to delete or rename a playlist with an invalid identifier, **Then** the system returns an explicit error message and a non-zero exit code.

---

### User Story 4 - Playlist content manipulation by LLM agent (Priority: P2)

An LLM agent can populate and modify the content of an existing playlist: add all tracks from an album, add an individual track, or remove a track from the playlist. The system confirms each action with a success message.

**Why this priority**: This is the final action in the complete workflow (search -> create playlist -> populate). It depends on the previous features. Per-track add/remove offers fine granularity for curated playlists.

**Independent Test**: Can be tested by creating a playlist, adding an album or track to it, then removing a track and verifying the result.

**Acceptance Scenarios**:

1. **Given** a valid authenticated session and an existing playlist, **When** the agent adds an album via its identifier to the playlist via its identifier, **Then** all tracks from the album are added to the playlist and a confirmation message is displayed.
2. **Given** a valid authenticated session and an existing playlist, **When** the agent adds a track via its identifier to the playlist via its identifier, **Then** the track is added to the playlist and a confirmation message is displayed.
3. **Given** a valid authenticated session and a playlist containing tracks, **When** the agent removes a track from the playlist by providing the track and playlist identifiers, **Then** the track is removed from the playlist and a confirmation message is displayed.
4. **Given** a valid authenticated session, **When** the agent attempts to add or remove an item with an invalid identifier, **Then** the system returns an explicit error message and a non-zero exit code.
5. **Given** a valid authenticated session, **When** the agent attempts to remove a track that is not in the playlist, **Then** the system returns an explicit error message and a non-zero exit code.

---

### User Story 5 - Automatic session refresh (Priority: P3)

When executing any command (except authentication), the system loads the session from the local file. If the access token is expired, the system automatically refreshes it in the background, updates the session file, then executes the requested command. The LLM agent is unaware of this process.

**Why this priority**: Ensures continuity of use without human intervention, but is not critical for initial use (the initial session is valid).

**Independent Test**: Can be tested by manually modifying the token expiration date in the session file, then executing a command and verifying that the token is refreshed and the command executes normally.

**Acceptance Scenarios**:

1. **Given** a session file with an expired token but a valid refresh token, **When** the agent executes a command, **Then** the system refreshes the token automatically, updates the session file, and executes the command normally.
2. **Given** a session file with both the token and refresh token expired, **When** the agent executes a command, **Then** the system returns an error message indicating the administrator must re-run authentication.

---

### User Story 6 - User library management by LLM agent (Priority: P3)

An LLM agent can add or remove artists, albums and tracks from the user's personal library (favorites). This allows saving items for quick access, independently of playlists.

**Why this priority**: Library management is a complementary feature to playlists. It enriches the experience but is not critical for the main workflow.

**Independent Test**: Can be tested by adding an artist to the library, verifying the confirmation message, then removing it.

**Acceptance Scenarios**:

1. **Given** a valid authenticated session, **When** the agent adds an artist to the library via its identifier, **Then** the artist is added to favorites and a confirmation message is displayed.
2. **Given** a valid authenticated session, **When** the agent removes an artist from the library via its identifier, **Then** the artist is removed from favorites and a confirmation message is displayed.
3. **Given** a valid authenticated session, **When** the agent adds an album to the library via its identifier, **Then** the album is added to favorites and a confirmation message is displayed.
4. **Given** a valid authenticated session, **When** the agent removes an album from the library via its identifier, **Then** the album is removed from favorites and a confirmation message is displayed.
5. **Given** a valid authenticated session, **When** the agent adds a track to the library via its identifier, **Then** the track is added to favorites and a confirmation message is displayed.
6. **Given** a valid authenticated session, **When** the agent removes a track from the library via its identifier, **Then** the track is removed from favorites and a confirmation message is displayed.
7. **Given** a valid authenticated session, **When** the agent attempts to add or remove an item with an invalid identifier, **Then** the system returns an explicit error message and a non-zero exit code.

---

### Edge Cases

- What happens if the session file is corrupted or unreadable? The system must return an explicit error message requesting re-authentication.
- What happens if the network connection is interrupted during a command? The system must return an explicit error message describing the connectivity issue.
- What happens if a required argument is missing from a command? The system must display a clear usage message on stderr and return a non-zero exit code.
- What happens if the agent provides an empty playlist name? The system must return a validation error.
- What happens if internal logs from the underlying library pollute stdout? The system must isolate these logs so that only expected results or planned error messages are visible on stdout.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a human to launch an interactive authentication flow that displays a login URL in the terminal.
- **FR-002**: The system MUST save session credentials (access token, refresh token) persistently in a local file after successful authentication.
- **FR-003**: The system MUST restrict session file permissions so that only the owner can read and modify it.
- **FR-004**: The system MUST allow searching for an artist by name and return a list of results with the name and unique identifier of each artist.
- **FR-005**: The system MUST allow searching for an album by name and return a list of results with the album name, artist name, release year and unique identifier of each album.
- **FR-017**: The system MUST allow searching for a track by name and return a list of results with the track name, artist name and unique identifier of each track.
- **FR-006**: The system MUST allow listing the user's created playlists with their name and unique identifier.
- **FR-007**: The system MUST allow creating a new playlist by providing a name (required) and a description (optional), and return the identifier of the created playlist.
- **FR-008**: The system MUST allow adding all tracks from an album to an existing playlist by providing the album and playlist identifiers.
- **FR-016**: The system MUST allow adding an individual track to an existing playlist by providing the track and playlist identifiers.
- **FR-018**: The system MUST allow renaming an existing playlist by providing its identifier and a new name.
- **FR-019**: The system MUST allow deleting an existing playlist by providing its identifier.
- **FR-020**: The system MUST allow removing a track from an existing playlist by providing the track and playlist identifiers.
- **FR-021**: The system MUST allow adding an artist to the user's library (favorites) by providing its identifier.
- **FR-022**: The system MUST allow removing an artist from the user's library by providing its identifier.
- **FR-023**: The system MUST allow adding an album to the user's library by providing its identifier.
- **FR-024**: The system MUST allow removing an album from the user's library by providing its identifier.
- **FR-025**: The system MUST allow adding a track to the user's library by providing its identifier.
- **FR-026**: The system MUST allow removing a track from the user's library by providing its identifier.
- **FR-015**: The system MUST offer two output modes: human-readable text by default and structured JSON via a global `--json` option. Both modes must contain the same information (name, identifier, etc.).
- **FR-009**: The system MUST return exit code 0 on success and a non-zero code on error.
- **FR-010**: The system MUST display explicit error messages on stderr when an argument is missing or invalid.
- **FR-011**: The system MUST return a specific error message when a command (other than authentication) is executed without a valid session, indicating the administrator must first run authentication.
- **FR-012**: The system MUST automatically refresh an expired access token in the background before executing a command, if the refresh token is still valid.
- **FR-013**: The system MUST isolate the underlying library's logs from stdout, so that the LLM agent only receives expected results or planned error messages.
- **FR-014**: The system MUST be contained in a single, self-contained file.

### Key Entities

- **Session**: Represents the user's authenticated connection to Tidal. Contains an access token, a refresh token and an expiration date. Persisted in a secured local file.
- **Artist**: A musician or group in the Tidal catalog. Identified by a name and a unique identifier.
- **Album**: A music album in the Tidal catalog. Identified by a name, an associated artist, a release year and a unique identifier. Contains a set of tracks.
- **Playlist**: An ordered collection of tracks created by the user. Identified by a name, an optional description and a unique identifier. Can be renamed or deleted.
- **Library (Favorites)**: The user's personal collection containing saved artists, albums and tracks. Provides quick access independently of playlists.
- **Track**: An individual music piece. Identified by a name, an associated artist and a unique identifier. Can be added individually to a playlist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The LLM agent can execute the complete workflow (search artist -> search album -> create playlist -> add album to playlist) autonomously, without human intervention, in fewer than 5 distinct commands.
- **SC-002**: 100% of commands return an appropriate exit code (0 for success, non-zero for error) and a message interpretable by an LLM.
- **SC-003**: Stdout never contains parasitic logs from the underlying library; only expected results or planned error messages are visible.
- **SC-004**: The session file is created with restricted permissions (accessible only by the owner).
- **SC-005**: Initial authentication can be completed by a human in under 2 minutes (excluding browser navigation and validation time).
- **SC-006**: Searches return results with name and identifier in human-readable text by default, and in structured JSON via the `--json` option, both formats being directly usable by an LLM agent without post-processing.
- **SC-007**: Token refresh occurs automatically without human intervention or error messages visible to the LLM agent.

## Assumptions

- The tool will be used primarily on Unix/macOS systems where file permissions (mode 600) are natively supported.
- The human user has an active Tidal account with a valid subscription.
- The LLM agent executes commands sequentially (no concurrent simultaneous calls).
- The underlying library for communicating with the Tidal API natively handles the OAuth flow and token refresh.
- Search results are limited to a reasonable number of items (the first 10-20 results) to remain readable by an LLM.
- The session file is stored in the same directory as the script.

## Scope

### Included

- Interactive OAuth authentication (human)
- Artist search by name
- Album search by name (with release year in results)
- Track search by name
- Listing user playlists
- Creating playlists (name + optional description)
- Adding complete albums to a playlist
- Adding individual tracks to a playlist
- Removing tracks from a playlist
- Renaming playlists
- Deleting playlists
- Adding and removing artists, albums and tracks from the library (favorites)
- Automatic session refresh management
- Error handling with explicit messages
- Internal log isolation

### Excluded

- Music playback/streaming
- Graphical or interactive interface
- Multi-user management
- Advanced search with multiple filters (genre, year, etc.)
