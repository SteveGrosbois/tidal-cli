# Quickstart: CLI Skills Directory

## Prerequisites

- `tidal-cli` installed and in PATH (`pip install -e .` from project root)
- Claude Code CLI installed
- Tidal account authenticated (`tidal-cli auth`)

## File Structure

```
skills/
├── tidal-auth/SKILL.md
├── tidal-search/SKILL.md
├── tidal-playlist/SKILL.md
└── tidal-library/SKILL.md
```

## Creating a Skill

1. Create the skill directory:
   ```bash
   mkdir -p skills/tidal-search
   ```

2. Create `SKILL.md` with frontmatter and instructions:
   ```yaml
   ---
   name: tidal-search
   description: Search for artists, albums, or tracks on Tidal
   allowed-tools: Bash, Read, Grep
   argument-hint: "<artist|album|track> <query>"
   ---

   # Tidal Search
   ...instructions...
   ```

3. The skill is auto-discovered — invoke with `/tidal-search Daft Punk`

## Testing a Skill

1. Open Claude Code in the project directory
2. Type `/tidal-search artist Daft Punk`
3. Verify formatted results appear (not raw JSON)
4. Test error case: `/tidal-search artist ""` — should show validation error

## Verification Checklist

- [ ] All 4 skill directories exist under `skills/`
- [ ] Each `SKILL.md` has valid YAML frontmatter
- [ ] Each skill is visible via `/` autocomplete in Claude Code
- [ ] Each skill correctly executes the underlying CLI command
- [ ] JSON output is parsed and presented as formatted text
- [ ] Error messages are user-friendly
