# Contract: Skill File Format

Each skill file MUST conform to this structure:

```yaml
---
name: tidal-<group>
description: <trigger description for auto-invocation>
allowed-tools: Bash, Read, Grep
argument-hint: "<expected arguments>"
---

# <Skill Title>

<Brief description of what this skill does>

## Commands

<For each CLI command covered by this skill:>
### <Command Name>
- **Usage**: `tidal-cli [--json] <command> <subcommand> [options]`
- **Arguments**: <list of required/optional arguments>
- **Output**: <description of JSON output fields>

## Instructions

<Step-by-step instructions for Claude:>
1. Parse user intent from $ARGUMENTS
2. Map to the appropriate CLI command
3. Execute with --json flag
4. Parse JSON output
5. Present results in formatted markdown (table for lists, confirmation for actions)

## Error Handling

<Instructions for handling CLI errors:>
- If exit code is non-zero, read stderr
- Match error message patterns and present user-friendly explanation
- For authentication errors, direct user to /tidal-auth
```

## Naming Convention

- Directory name: `tidal-<group>` (e.g., `tidal-search`)
- File: `SKILL.md` (exactly this name, uppercase)
- Slash command: `/tidal-<group>` (auto-derived from directory name or `name` frontmatter)

## Output Formatting Convention

- **Search results**: Markdown table with columns matching JSON fields
- **Single item actions** (create, rename, delete, add, remove): Confirmation message with key details
- **Errors**: Prefixed with a clear label, with actionable guidance
