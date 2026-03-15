# Feature Specification: CLI Skills Directory

**Feature Branch**: `002-cli-skills`
**Created**: 2026-03-15
**Status**: Draft
**Input**: User description: "I want to create a skills directory at the project root. These skills must cover all tidal-cli functionalities."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search for music via a skill (Priority: P1)

The user invokes a search skill (artist, album, or track) from Claude Code by typing a dedicated slash command. The skill builds and executes the appropriate tidal-cli command, then presents the results in a readable format.

**Why this priority**: Search is the main entry point for any music interaction. Without search, no other action (playlist management, favorites) is possible.

**Independent Test**: Can be tested by invoking the search skill with an artist name and verifying the results display correctly.

**Acceptance Scenarios**:

1. **Given** the user is authenticated on Tidal, **When** they invoke the search skill with an artist name, **Then** the results display matching artists with their ID and name.
2. **Given** the user is authenticated on Tidal, **When** they invoke the search skill with an album name, **Then** the results display matching albums with ID, name, artist, and year.
3. **Given** the user is authenticated on Tidal, **When** they invoke the search skill with a track name, **Then** the results display matching tracks with ID, name, and artist.
4. **Given** no match exists for the query, **When** the user invokes the search skill, **Then** a clear message indicates no results were found.

---

### User Story 2 - Manage playlists via skills (Priority: P2)

The user uses dedicated skills to list, create, rename, delete playlists, and to add or remove tracks/albums from an existing playlist. The skill guides the user if parameters are missing.

**Why this priority**: Playlist management is the richest CLI feature and benefits the most from a guided conversational interface.

**Independent Test**: Can be tested by creating a playlist via the skill, then adding a track and verifying the playlist appears in the list.

**Acceptance Scenarios**:

1. **Given** the user is authenticated, **When** they invoke the playlist listing skill, **Then** all their playlists are displayed with ID, name, and track count.
2. **Given** the user is authenticated, **When** they invoke the playlist creation skill with a name, **Then** the playlist is created and a confirmation ID is displayed.
3. **Given** the user provides a playlist ID and a track ID, **When** they invoke the add track skill, **Then** the track is added to the playlist with a confirmation message.
4. **Given** the user provides a playlist ID and an album ID, **When** they invoke the add album skill, **Then** all album tracks are added with the track count indicated.
5. **Given** the user provides a non-existent playlist ID, **When** they invoke a playlist management skill, **Then** a clear error message is displayed.

---

### User Story 3 - Manage favorites via skills (Priority: P3)

The user uses skills to add or remove artists, albums, or tracks from their Tidal library (favorites).

**Why this priority**: Favorites management completes the user experience but is less frequently used than search and playlists.

**Independent Test**: Can be tested by adding an artist to favorites via the skill and verifying the confirmation message.

**Acceptance Scenarios**:

1. **Given** the user is authenticated and provides an artist ID, **When** they invoke the add to favorites skill, **Then** the artist is added to the library with a confirmation message.
2. **Given** the user is authenticated and provides a track ID, **When** they invoke the remove from favorites skill, **Then** the track is removed from the library with a confirmation message.
3. **Given** the user provides a non-existent ID, **When** they invoke the favorites management skill, **Then** an explicit error message is displayed.

---

### User Story 4 - Authenticate via a skill (Priority: P1)

The user invokes an authentication skill that launches the interactive Tidal OAuth process. The skill guides the user through the login steps.

**Why this priority**: Authentication is a prerequisite for all other features. Without an active session, no other skill works.

**Independent Test**: Can be tested by invoking the authentication skill and verifying the session file is created.

**Acceptance Scenarios**:

1. **Given** the user is not yet authenticated, **When** they invoke the authentication skill, **Then** the OAuth process is launched and the login URL is displayed.
2. **Given** the user is already authenticated with a valid session, **When** they invoke the authentication skill, **Then** they are informed the session is already active.

---

### Edge Cases

- What happens if the user invokes a skill without being authenticated? The skill must display a clear message directing them to the authentication skill.
- What happens if the network connection is unavailable? The skill must relay the CLI's network error message.
- What happens if the user provides invalid arguments (non-numeric ID, empty name)? The skill must relay the CLI's validation messages.
- What happens if the access token expires during use? Transparent token refresh must work without user intervention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST contain a `skills/` directory at the root, containing Claude Code skill files.
- **FR-002**: Each skill MUST be a standalone Markdown file with a YAML frontmatter defining its name, description, and instructions.
- **FR-003**: A search skill MUST allow searching for artists, albums, and tracks via the `tidal-cli search` command.
- **FR-004**: A playlist management skill MUST cover operations: list, create, rename, delete, add album, add track, remove track.
- **FR-005**: A favorites management skill MUST allow adding and removing artists, albums, and tracks from the library.
- **FR-006**: An authentication skill MUST guide the user through the Tidal OAuth process.
- **FR-007**: Each skill MUST use the CLI's `--json` mode to parse results reliably.
- **FR-008**: Each skill MUST handle CLI errors (missing authentication, network, entity not found) and present them clearly to the user.
- **FR-009**: Skills MUST follow the standard Claude Code skill format (Markdown file with frontmatter and instructions).
- **FR-010**: Skills MUST be referenced in the project configuration to be discoverable via slash commands.
- **FR-011**: Each skill invocation MUST be atomic — performing one operation and returning its result. Skills MUST NOT chain follow-up actions or prompt for additional operations.

### Key Entities

- **Skill**: A Markdown file describing a capability invocable via Claude Code, with a name, a trigger description, and execution instructions.
- **CLI Command**: The underlying tidal-cli command executed by the skill (e.g., `tidal-cli search artist`, `tidal-cli playlist create`).
- **JSON Result**: Structured output from the CLI in `--json` mode, parsed by the skill to format the response.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of existing tidal-cli commands (13 commands) are covered by at least one skill.
- **SC-002**: Each skill can be invoked by the user via a slash command in Claude Code.
- **SC-003**: Results from each skill are presented in a formatted, readable way (no raw JSON displayed to the user).
- **SC-004**: CLI errors are intercepted and reformulated into understandable messages in 100% of documented error cases.
- **SC-005**: A user unfamiliar with the CLI can complete a search and a playlist addition using only skills, without knowing the underlying CLI commands.

## Clarifications

### Session 2026-03-15

- Q: Should the 13 CLI commands be grouped into a few multi-purpose skills or split into individual single-purpose skills? → A: One skill per functional group (4 skills: `tidal-auth`, `tidal-search`, `tidal-playlist`, `tidal-library`).
- Q: Should skills support chained multi-step workflows or be atomic (one operation per invocation)? → A: Atomic — each invocation performs one operation and returns results. User chains skills manually in conversation.

## Assumptions

- Claude Code skills use the Markdown format with YAML frontmatter as documented in the Claude Code specification.
- The `tidal-cli` CLI is installed and accessible in the execution environment's PATH.
- OAuth authentication requires human interaction (browser) and cannot be fully automated by the skill.
- The CLI's `--json` mode is the preferred method for parsing results in skills, as it provides structured and predictable output.
- Skills are organized as one skill per functional group, resulting in 4 skills: `tidal-auth`, `tidal-search`, `tidal-playlist`, `tidal-library`.
