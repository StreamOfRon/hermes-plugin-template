# AGENTS.md — Instructions for AI Coding Agents

This project is a **Hermes plugin template** created from `hermes-plugin-template`.
It provides boilerplate for all three Hermes extension layers: **Skills**, **Tools**, and **Plugins**.

## Project Structure

```
├── plugin/                 # PLUGIN LAYER — Python code + manifest
│   ├── plugin.yaml         # Plugin manifest (name, version, tools, hooks)
│   ├── __init__.py         # register(ctx) entry point
│   ├── tools.py            # Tool handler implementations
│   └── schemas.py          # OpenAI-format tool schema definitions
│
├── skill/                  # SKILL LAYER — Markdown instructions for AI
│   └── SKILL.md            # Skill definition with YAML frontmatter
│
├── tests/                  # TEST SCAFFOLDING
│   ├── test_plugin.py      # Plugin loading + tool registration tests
│   └── test_skill.py       # Skill frontmatter + structure tests
│
├── pyproject.toml          # Pip distribution config
├── Makefile                # Convenience targets
└── AGENTS.md               # This file
```

## How to Add a New Tool

1. **Define the schema** in `plugin/schemas.py`:
   ```python
   MY_TOOL_SCHEMA = {
       "name": "my_plugin_my_tool",
       "description": "What this tool does",
       "parameters": {
           "type": "object",
           "properties": {
               "param_name": {"type": "string", "description": "..."},
           },
           "required": ["param_name"],
       },
   }
   ```

2. **Implement the handler** in `plugin/tools.py`:
   ```python
   def my_tool_handler(args, **kwargs):
       try:
           # Process args, return json.dumps(result)
           return json.dumps({"status": "success", "data": ...})
       except Exception as e:
           return json.dumps({"status": "error", "error": str(e)})
   ```

3. **Register in `plugin/__init__.py`**:
   ```python
   from .schemas import MY_TOOL_SCHEMA
   from .tools import my_tool_handler

   def register(ctx):
       ctx.register_tool(schema=MY_TOOL_SCHEMA, handler=my_tool_handler)
   ```

4. **Update `plugin/plugin.yaml`**:
   ```yaml
   provides_tools:
     - my_plugin_my_tool
   ```

## How to Add a New Skill

1. Create a directory under `~/.hermes/skills/<skill-name>/`
2. Add a `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: What this skill does
   ---
   ```
3. Required frontmatter fields: `name`, `description`
4. Optional fields: `author`, `version`, `tags`, `requires_tools`, `provides_commands`
5. Standard sections: `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`
6. Field constraints: `name` ≤ 50 chars, `description` ≤ 200 chars

## How to Add Lifecycle Hooks

In `plugin/__init__.py`:
```python
def on_session_start(session, **kwargs):
    # Hook logic here
    pass

def register(ctx):
    # ... tool registration ...
    ctx.register_hook("on_session_start", on_session_start)
```

## Handler Contract

- **Signature**: `def handler(args, **kwargs) -> str`
- **Return**: MUST return a JSON-encoded string (`json.dumps(...)`)
- **Errors**: MUST NOT raise exceptions; catch and return error JSON
- **args**: Dict of parameters matching the schema definition

## Testing Patterns

- Use `tmp_path` fixture for temporary directories
- Monkeypatch `HERMES_HOME` to avoid affecting real installation
- Create `PluginManager()` directly (not global singleton)
- Test: discovery, loading, tool registration, tool execution, hook invocation

```python
@pytest.fixture
def hermes_home(tmp_path, monkeypatch):
    hermes = tmp_path / ".hermes"
    hermes.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes))
    return hermes
```

## Common Pitfalls

- **Hardcoded `~/.hermes`**: Never hardcode paths; use `HERMES_HOME` env var
- **Missing `name` in schema**: Every tool schema MUST have a `name` field
- **Raising in handlers**: Handlers must catch all exceptions and return error JSON
- **Non-JSON returns**: Handlers MUST return `json.dumps(...)`, not raw strings/dicts
- **Duplicate tool names**: Tool names must be unique across all loaded plugins
- **Missing frontmatter delimiters**: SKILL.md must start and end frontmatter with `---`

## Key Hermes Source Files (for reference)

When implementing advanced patterns, reference the Hermes agent source:
- Plugin loading: `hermes_agent/plugins/manager.py`
- Tool execution: `hermes_agent/plugins/context.py`
- Skill loading: `hermes_agent/skills/`
- Hook system: Check for hook registration in the plugin context
