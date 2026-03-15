# Implementation Plan: CLI Skills Directory

**Branch**: `002-cli-skills` | **Date**: 2026-03-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-cli-skills/spec.md`

## Summary

Create 4 Claude Code skills (Markdown files with YAML frontmatter) under `skills/` at the project root that wrap all 13 tidal-cli commands. Each skill covers one functional group (auth, search, playlist, library), uses `--json` mode for reliable parsing, and presents formatted results to the user. Skills are atomic — one operation per invocation.

## Technical Context

**Language/Version**: Markdown (YAML frontmatter) — no code to compile
**Primary Dependencies**: Claude Code skills system, `tidal-cli` CLI (Python 3.10+ / Typer)
**Storage**: N/A — skills are static files
**Testing**: Manual invocation via Claude Code slash commands
**Target Platform**: Claude Code CLI (macOS/Linux)
**Project Type**: CLI skill configuration
**Performance Goals**: N/A — skills are prompt templates, performance depends on CLI execution
**Constraints**: Skills placed in `skills/` at project root, following the [googleworkspace/cli](https://github.com/googleworkspace/cli) reference pattern
**Scale/Scope**: 4 skill files covering 13 CLI commands

## Constitution Check

*No constitution file found. Gates skipped.*

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-skills/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── skill-format.md  # Skill file contract
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
skills/
├── tidal-auth/
│   └── SKILL.md         # Authentication skill (1 command)
├── tidal-search/
│   └── SKILL.md         # Search skill (3 commands: artist, album, track)
├── tidal-playlist/
│   └── SKILL.md         # Playlist management skill (7 commands)
└── tidal-library/
    └── SKILL.md          # Library/favorites skill (2 commands)
```

**Structure Decision**: Skills placed in `skills/` at the project root, following the pattern from the [googleworkspace/cli](https://github.com/googleworkspace/cli) reference project. Each skill gets its own directory with a `SKILL.md` file.
