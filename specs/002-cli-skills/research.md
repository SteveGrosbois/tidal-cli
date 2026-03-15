# Research: CLI Skills Directory

## R1: Claude Code Skill File Format

**Decision**: Skills use Markdown files with YAML frontmatter, placed in `skills/<skill-name>/SKILL.md` at the project root.

**Rationale**: Follows the pattern established by the [googleworkspace/cli](https://github.com/googleworkspace/cli) reference project, which places all skills in a top-level `skills/` directory. This keeps skills visible and co-located with the project source, rather than hidden under `.claude/`.

**Alternatives considered**:
- `.claude/skills/`: Standard Claude Code convention for project-specific auto-discovery. Rejected in favor of root-level visibility matching the reference project.
- `~/.claude/skills/`: Personal (cross-project) scope. Not appropriate for project-specific skills.

**Reference**: googleworkspace/cli uses `skills/<name>/SKILL.md` with frontmatter fields including `name`, `description`, `version`, and `metadata`.

## R2: Skill Frontmatter Fields

**Decision**: Use these frontmatter fields per skill:
- `name`: Slash command name (e.g., `tidal-search`)
- `description`: Trigger description for auto-invocation and user clarity
- `allowed-tools`: `Bash, Read, Grep` — tools the skill can use without permission prompts
- `argument-hint`: Show expected arguments in autocomplete

**Rationale**: Minimal required fields. `disable-model-invocation` left as default (false) so Claude can suggest skills contextually.

**Alternatives considered**:
- `context: fork` (isolated subagent): Adds overhead, unnecessary for simple CLI wrappers.
- `model: opus`: Unnecessary, inherits from session.

## R3: Skill Content and Command Execution

**Decision**: Each skill's Markdown body contains:
1. A description of what the skill does
2. Instructions for Claude on how to parse user intent and map to CLI commands
3. The exact `tidal-cli` commands to run with `--json` flag
4. Error handling instructions referencing CLI error messages

**Rationale**: Skills are prompt templates — Claude reads the instructions and executes accordingly using the Bash tool.

**Alternatives considered**:
- `!`command`` syntax (pre-processing): Runs before Claude sees the skill — not suitable since we need Claude to interpret user arguments first.
- External scripts in `scripts/`: Over-engineering for simple CLI wrappers.

## R4: String Substitutions

**Decision**: Use `$ARGUMENTS` to capture user input passed after the slash command.

**Rationale**: Built-in Claude Code variable. `$ARGUMENTS[0]`, `$ARGUMENTS[1]` available for positional arguments.

## R5: Skill Directory Structure

**Decision**: Simple structure — one `SKILL.md` per skill directory at project root, no additional files needed.

```
skills/
├── tidal-auth/SKILL.md
├── tidal-search/SKILL.md
├── tidal-playlist/SKILL.md
└── tidal-library/SKILL.md
```

**Rationale**: Each skill wraps a small set of CLI commands. No helper scripts, reference docs, or external resources needed.

**Alternatives considered**:
- Adding `reference.md` with CLI help output: Unnecessary since skills contain all needed instructions inline.
- Adding `scripts/`: Over-engineering — the CLI itself is the script.
