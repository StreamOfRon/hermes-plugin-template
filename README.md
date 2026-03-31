# Hermes Plugin Template

A boilerplate template for building [Hermes](https://github.com/streamofron/hermes-agent) extensions. Provides scaffolding for all three Hermes extension layers: **Skills**, **Tools**, and **Plugins**.

## How to Use This Template

1. Click **"Use this template"** on GitHub (or fork this repository)
2. Clone your new repository locally
3. Customize the files (see [Quick Start](#quick-start))
4. Install into your Hermes instance

## Quick Start

```bash
# 1. Clone your repository
git clone git@github.com:your-org/your-hermes-plugin.git
cd your-hermes-plugin

# 2. Install dev dependencies
make dev-install

# 3. Install plugin to local Hermes
make install-local

# 4. Install skill to local Hermes
make install-skill

# 5. Verify
hermes plugins list
```

## Extension Layers

### Skill Layer (`skill/`)

Skills are Markdown files with YAML frontmatter that instruct AI agents on when and how to behave. They define slash commands, provide procedural knowledge, and reference external resources.

**Use when**: You want to add AI behavior instructions, slash commands, or procedural workflows.

```
skill/
└── SKILL.md        # Skill definition with frontmatter
```

### Tool Layer (`plugin/`)

Tools are Python functions exposed to the AI model as function-calling capabilities. Each tool has a schema (OpenAI format) and a handler implementation.

**Use when**: You want the AI to call your code — API integrations, data processing, external services.

```
plugin/
├── plugin.yaml     # Manifest (name, version, tools, hooks)
├── __init__.py     # register(ctx) entry point
├── tools.py        # Handler implementations
└── schemas.py      # OpenAI-format schemas
```

### Plugin Layer (hooks)

Plugins can register lifecycle hooks that run at specific points in the Hermes session lifecycle (session start, message received, etc.).

**Use when**: You need to react to lifecycle events — logging, session setup, message preprocessing.

## Running Tests

```bash
# Run all tests
make test

# Or directly with pytest
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_plugin.py -v
python -m pytest tests/test_skill.py -v
```

## Distribution

### Via GitHub (recommended for teams)

1. Push your customized plugin to a GitHub repository
2. Users clone and run `make install-local`

### Via pip (recommended for public distribution)

```bash
# Build and install
pip install .

# Or install from PyPI (after publishing)
pip install your-hermes-plugin
```

The `pyproject.toml` is configured with the `hermes_agent.plugins` entry point for automatic discovery.

### Via Hermes Skills Hub

Publish your `SKILL.md` to the [Hermes Skills Hub](https://github.com/streamofron/hermes-skills) for community discovery.

## Adding New Tools

See `AGENTS.md` for detailed instructions on adding tools, skills, and hooks.

Quick summary:
1. Add schema to `plugin/schemas.py`
2. Add handler to `plugin/tools.py`
3. Register in `plugin/__init__.py`
4. Update `plugin.yaml` `provides_tools` list

## License

MIT — see [LICENSE](LICENSE)
