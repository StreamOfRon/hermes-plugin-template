# AGENTS.md — Hermes Plugin Template

Hermes plugins are imported directly from GitHub by path convention — no Python package building required.

## Project Structure

```
├── __init__.py             # Plugin entry point — register(ctx) function
├── plugin.yaml             # Plugin manifest (name, version, tools, hooks)
├── tools.py                # Tool handler implementations
├── schemas.py              # OpenAI-format tool schema definitions
├── skill/SKILL.md          # Bundled skill with YAML frontmatter
├── scripts/install.py      # Install plugin/skill to local HERMES_HOME
├── tests/                  # Test scaffolding
└── AGENTS.md               # This file
```

Plugin files live at the repository root. The entire directory is the plugin.

## Adding a Tool

1. Define schema in `schemas.py` — see existing schema for format
2. Implement handler in `tools.py` — handlers must return JSON strings via `json.dumps()`
3. Register in `__init__.py` using `ctx.register_tool()`
4. Add tool name to `plugin.yaml` under `provides_tools`

Handler requirements:
- Signature: `def handler(args: dict, **kwargs) -> str`
- Return: JSON-encoded string via `json.dumps()`
- Errors: Catch all exceptions and return error JSON

## Adding a Skill

1. Create `skill/SKILL.md` with YAML frontmatter (see existing file for format)
2. Install during plugin registration via `_install_skill()` helper in `__init__.py`

Required frontmatter fields: `name`, `description`  
Optional fields: `author`, `version`, `tags`, `requires_tools`, `provides_commands`

## Adding Lifecycle Hooks

Register hooks in `__init__.py` using `ctx.register_hook()`:
- `pre_tool_call` / `post_tool_call` — wrap tool execution
- `pre_llm_call` / `post_llm_call` — wrap LLM calls
- `on_session_start` / `on_session_end` — session lifecycle

See `__init__.py` for hook registration examples.

## Testing

Tests validate plugin structure and handler contracts:
- `tests/test_plugin.py` — plugin.yaml parsing, handler contracts
- `tests/test_skill.py` — SKILL.md frontmatter validation

## Common Pitfalls

- Never hardcode `~/.hermes` — use `HERMES_HOME` environment variable
- Tool schemas must include a `name` field
- Handlers must catch exceptions and return error JSON (never raise)
- `toolset` parameter should be the plugin name, not the tool name
- Handlers must accept `**kwargs` for forward compatibility
- SKILL.md must have frontmatter delimited by `---`

## Reference

- Hermes plugin loading: `hermes_cli/plugins.py`
- Plugin context API: `PluginContext` class in `hermes_cli/plugins.py`
- Skill loading: `hermes_cli/skills_config.py`
- Hook system: `invoke_hook()` in `hermes_cli/plugins.py`
