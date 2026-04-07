#!/usr/bin/env python3
"""Install plugin and skill to local HERMES_HOME.

Usage:
    uv run scripts/install.py --local       Install plugin + skill
    uv run scripts/install.py --plugin      Install plugin only
    uv run scripts/install.py --skill       Install skill only
    uv run scripts/install.py --dry-run     Show what would be installed
"""

import argparse
import shutil
import sys
from pathlib import Path


def get_hermes_home() -> Path:
    """Get HERMES_HOME path, respecting env var or defaulting to ~/.hermes."""
    import os
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".hermes"


def install_plugin(plugin_name: str, dry_run: bool = False) -> bool:
    """Copy plugin files to HERMES_HOME/plugins/<name>/."""
    root = Path(__file__).parent.parent
    plugin_files = ["plugin.yaml", "__init__.py", "schemas.py", "tools.py"]

    for f in plugin_files:
        if not (root / f).exists():
            print(f"Error: {f} not found at {root}", file=sys.stderr)
            return False

    dest = get_hermes_home() / "plugins" / plugin_name
    if dry_run:
        print(f"[dry-run] Would install plugin to: {dest}")
        for f in plugin_files:
            print(f"  - {f}")
        return True

    if dest.exists():
        print(f"Plugin already installed at {dest} (skipping)")
        print(f"  Remove it first to reinstall: rm -rf {dest}")
        return True

    dest.mkdir(parents=True, exist_ok=True)
    for f in plugin_files:
        shutil.copy2(root / f, dest / f)

    print(f"Plugin installed to: {dest}")
    return True


def install_skill(skill_name: str, dry_run: bool = False) -> bool:
    """Copy skill to HERMES_HOME/skills/<name>/."""
    skill_file = Path(__file__).parent.parent / "skill" / "SKILL.md"
    if not skill_file.exists():
        print("Warning: skill/SKILL.md not found, skipping skill install")
        return True

    dest = get_hermes_home() / "skills" / skill_name / "SKILL.md"
    if dry_run:
        print(f"[dry-run] Would install skill to: {dest}")
        return True

    if dest.exists():
        print(f"Skill already installed at {dest} (skipping)")
        print(f"  Remove it first to reinstall: rm -rf {dest.parent}")
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill_file, dest)

    print(f"Skill installed to: {dest}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Install plugin and skill to local HERMES_HOME")
    parser.add_argument("--local", action="store_true", help="Install both plugin and skill")
    parser.add_argument("--plugin", action="store_true", help="Install plugin only")
    parser.add_argument("--skill", action="store_true", help="Install skill only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")
    args = parser.parse_args()

    if not args.local and not args.plugin and not args.skill:
        args.local = True  # default: install everything

    # Read plugin name from plugin.yaml
    plugin_yaml = Path(__file__).parent.parent / "plugin.yaml"
    try:
        import yaml
        manifest = yaml.safe_load(plugin_yaml.read_text())
        plugin_name = manifest.get("name", "unknown_plugin")
    except ImportError:
        # Fallback: parse YAML manually for the name field
        content = plugin_yaml.read_text()
        for line in content.splitlines():
            if line.startswith("name:"):
                plugin_name = line.split(":", 1)[1].strip()
                break
        else:
            plugin_name = "unknown_plugin"

    # Derive skill name from plugin name (replace underscores with hyphens)
    skill_name = plugin_name.replace("_", "-")

    ok = True
    if args.local or args.plugin:
        ok = install_plugin(plugin_name, args.dry_run) and ok
    if args.local or args.skill:
        ok = install_skill(skill_name, args.dry_run) and ok

    if ok:
        if args.dry_run:
            print("\nDry run complete. Run without --dry-run to actually install.")
        else:
            print("\nDone. Restart Hermes and check /plugins to verify.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
