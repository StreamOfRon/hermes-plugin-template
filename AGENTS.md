# AGENTS.md — Instructions for AI Coding Agents

This project is a **Hermes plugin template** created from `hermes-plugin-template`.
It provides boilerplate for all three Hermes extension layers: **Skills**, **Tools**, and **Plugins**.

## Project Structure

```
├── __init__.py             # PLUGIN ENTRY — register(ctx) function
├── plugin.yaml             # Plugin manifest (name, version, tools, hooks)
├── tools.py                # Tool handler implementations
├── schemas.py              # OpenAI-format tool schema definitions
│
├── skill/                  # SKILL LAYER — Markdown instructions for AI
│   └── SKILL.md            # Skill definition with YAML frontmatter
│
├── scripts/                # UTILITY SCRIPTS
│   └── install.py          # Install plugin/skill to local HERMES_HOME
│
├── tests/                  # TEST SCAFFOLDING
│   ├── test_plugin.py      # Plugin structure + handler contract tests
│   └── test_skill.py       # Skill frontmatter + structure tests
│
├── pyproject.toml          # Pip distribution config
├── ruff.toml               # Linting configuration
└── AGENTS.md               # This file
```

The plugin files (`__init__.py`, `plugin.yaml`, `tools.py`, `schemas.py`) live at the **repository root**, not in a subdirectory. This is the standard Hermes plugin layout — the entire directory is the plugin.

## How to Add a New Tool

1. **Define the schema** in `schemas.py`:
   ```python
   MY_TOOL_SCHEMA = {
       "name": "my_plugin_my_tool",
       "description": "What this tool does — be specific so the LLM knows when to use it",
       "parameters": {
           "type": "object",
           "properties": {
               "param_name": {"type": "string", "description": "..."},
           },
           "required": ["param_name"],
       },
   }
   ```

2. **Implement the handler** in `tools.py`:
   ```python
   def my_tool_handler(args: dict, **kwargs) -> str:
       try:
           # Process args, return json.dumps(result)
           return json.dumps({"status": "success", "data": ...})
       except Exception as e:
           return json.dumps({"status": "error", "error": str(e)})
   ```

3. **Register in `__init__.py`**:
   ```python
   from schemas import MY_TOOL_SCHEMA
   from tools import my_tool_handler

   def register(ctx):
       ctx.register_tool(
           name=MY_TOOL_SCHEMA["name"],
           toolset="my_plugin",        # plugin name, NOT tool name
           schema=MY_TOOL_SCHEMA,
           handler=my_tool_handler,
       )
   ```

4. **Update `plugin.yaml`**:
   ```yaml
   provides_tools:
     - my_plugin_my_tool
   ```

## How to Add a New Skill

### Where skills live

Skills are installed to `~/.hermes/skills/<skill-name>/SKILL.md` at runtime.
The `skill/` directory in this repo is a **bundled copy** that gets installed
when the plugin loads.

### Bundling a skill with your plugin

Include a `SKILL.md` in the `skill/` directory and install it during registration:

```python
import shutil
from pathlib import Path

def _install_skill():
    """Copy our skill to ~/.hermes/skills/ on first load."""
    try:
        from hermes_cli.config import get_hermes_home
        dest = get_hermes_home() / "skills" / "my-plugin" / "SKILL.md"
    except Exception:
        dest = Path.home() / ".hermes" / "skills" / "my-plugin" / "SKILL.md"
    if dest.exists():
        return  # don't overwrite user edits
    source = Path(__file__).parent / "skill" / "SKILL.md"
    if source.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

def register(ctx):
    ctx.register_tool(...)
    _install_skill()
```

### Creating a new skill file

1. Add a `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: What this skill does
   ---
   ```
2. Required frontmatter fields: `name`, `description`
3. Optional fields: `author`, `version`, `tags`, `requires_tools`, `provides_commands`
4. Standard sections: `## When to Use`, `## Procedure`, `## Pitfalls`, `## Verification`
5. Field constraints: `name` ≤ 50 chars, `description` ≤ 200 chars

## How to Add Lifecycle Hooks

In `__init__.py`:

```python
import logging
logger = logging.getLogger(__name__)

def on_session_start(session, **kwargs):
    logger.info("Session started: %s", session.id)

def register(ctx):
    # ... tool registration ...
    ctx.register_hook("on_session_start", on_session_start)
```

Available hooks:

| Hook | When | Arguments | Return |
|------|------|-----------|--------|
| `pre_tool_call` | Before any tool runs | `tool_name`, `args`, `task_id` | — |
| `post_tool_call` | After any tool returns | `tool_name`, `args`, `result`, `task_id` | — |
| `pre_llm_call` | Once per turn, before LLM loop | `session_id`, `user_message`, `conversation_history`, `is_first_turn`, `model`, `platform` | `{"context": "..."}` |
| `post_llm_call` | Once per turn, after LLM loop | `session_id`, `user_message`, `assistant_response`, `conversation_history`, `model`, `platform` | — |
| `on_session_start` | New session created | `session`, `model`, `platform` | — |
| `on_session_end` | End of session | `session`, `completed`, `interrupted`, `model`, `platform` | — |

The `pre_llm_call` hook can inject context: return a dict with `"context"` key to append to the system prompt.
If a hook crashes, it's logged and skipped; other hooks and the agent continue normally.

## Handler Contract

- **Signature**: `def handler(args: dict, **kwargs) -> str`
- **Return**: MUST return a JSON-encoded string (`json.dumps(...)`)
- **Errors**: MUST NOT raise exceptions; catch and return error JSON
- **args**: Dict of parameters matching the schema definition
- **kwargs**: Accept `**kwargs` for forward compatibility

## Testing Patterns

Tests validate plugin structure and handler contracts — **not** Hermes internals.

```python
# Test plugin.yaml parses correctly
import yaml
from pathlib import Path

def test_plugin_yaml():
    data = yaml.safe_load(Path("plugin.yaml").read_text())
    assert "name" in data
    assert "provides_tools" in data

# Test handler contract
import json
from tools import my_tool_handler

def test_handler_returns_json():
    result = my_tool_handler({"param": "value"})
    data = json.loads(result)
    assert data["status"] == "success"

def test_handler_never_raises():
    result = my_tool_handler({})
    data = json.loads(result)
    assert "status" in data  # error or success, but never an exception
```

## Common Pitfalls

- **Hardcoded `~/.hermes`**: Never hardcode paths; use `HERMES_HOME` env var
- **Missing `name` in schema**: Every tool schema MUST have a `name` field
- **Raising in handlers**: Handlers must catch all exceptions and return error JSON
- **Non-JSON returns**: Handlers MUST return `json.dumps(...)`, not raw strings/dicts
- **Duplicate tool names**: Tool names must be unique across all loaded plugins
- **Missing frontmatter delimiters**: SKILL.md must start and end frontmatter with `---`
- **Using tool name as toolset**: `toolset` should be the plugin name, not the tool name
- **Missing `**kwargs`**: Handlers must accept `**kwargs` for forward compatibility
- **Vague schema descriptions**: Be specific so the LLM knows when to use your tool
- **Not updating plugin.yaml**: Adding a tool requires updating both `schemas.py` and `plugin.yaml`

## Key Hermes Source Files (for reference)

When implementing advanced patterns, reference the Hermes agent source:
- Plugin loading: `hermes_cli/plugins.py`
- Plugin context: `PluginContext` class in `hermes_cli/plugins.py`
- Skill loading: `hermes_cli/skills_config.py`
- Hook system: `invoke_hook()` in `hermes_cli/plugins.py`
