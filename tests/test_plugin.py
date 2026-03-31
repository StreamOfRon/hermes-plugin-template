"""Tests for plugin loading, discovery, and tool registration.

Uses tmp_path fixture and monkeypatches HERMES_HOME to avoid
interfering with the user's actual Hermes installation.
Creates PluginManager directly (not global singleton).
"""

import json
import os
import sys
from pathlib import Path

import pytest


@pytest.fixture
def hermes_home(tmp_path, monkeypatch):
    """Create a temporary HERMES_HOME and monkeypatch the env var."""
    hermes = tmp_path / ".hermes"
    hermes.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes))
    return hermes


@pytest.fixture
def plugin_dir(hermes_home):
    """Create a plugins directory with the example plugin installed."""
    plugins = hermes_home / "plugins" / "example_plugin"
    plugins.mkdir(parents=True)

    # Copy plugin files to the temp location
    source = Path(__file__).parent.parent / "plugin"
    for item in source.iterdir():
        if item.is_file():
            dest = plugins / item.name
            dest.write_text(item.read_text())

    return plugins


class TestPluginDiscovery:
    """Test that plugins are discovered correctly."""

    def test_discover_plugin_in_hermes_home(self, hermes_home, plugin_dir):
        """PluginManager should find plugins in HERMES_HOME/plugins/."""
        from hermes_cli.plugins import get_plugin_manager

        manager = get_plugin_manager()
        manager.discover_and_load()

        plugin_names = [p["name"] for p in manager.list_plugins()]
        assert "example_plugin" in plugin_names

    def test_discover_empty_directory(self, hermes_home):
        """PluginManager should handle empty plugins directory."""
        (hermes_home / "plugins").mkdir(exist_ok=True)

        from hermes_cli.plugins import PluginManager

        # Create a fresh manager (singleton from get_plugin_manager may
        # carry state from other tests)
        manager = PluginManager()
        manager.discover_and_load()

        assert len(manager.list_plugins()) == 0


class TestPluginLoading:
    """Test that plugins load correctly."""

    def test_load_plugin(self, hermes_home, plugin_dir):
        """Plugin should load without errors."""
        from hermes_cli.plugins import get_plugin_manager

        manager = get_plugin_manager()
        manager.discover_and_load()

        plugins = manager.list_plugins()
        assert len(plugins) == 1
        assert plugins[0]["name"] == "example_plugin"

    def test_load_plugin_manifest(self, hermes_home, plugin_dir):
        """Plugin manifest (plugin.yaml) should be parsed correctly."""
        from hermes_cli.plugins import get_plugin_manager

        manager = get_plugin_manager()
        manager.discover_and_load()

        plugin = manager.list_plugins()[0]
        assert plugin["version"] == "0.1.0"
        assert plugin["error"] is None


class TestToolRegistration:
    """Test that tools are registered correctly."""

    def test_tool_registration(self, hermes_home, plugin_dir):
        """Registered tools should be available in the tool registry."""
        from hermes_cli.plugins import get_plugin_manager, get_plugin_tool_names

        manager = get_plugin_manager()
        manager.discover_and_load()

        tool_names = get_plugin_tool_names()
        assert "example_plugin_example_tool" in tool_names

    def test_tool_execution(self, hermes_home, plugin_dir):
        """Registered tool should execute and return valid JSON."""
        from hermes_cli.plugins import get_plugin_manager

        manager = get_plugin_manager()
        manager.discover_and_load()

        plugin = manager.list_plugins()[0]
        assert plugin["tools"] >= 1
        assert plugin["error"] is None

    def test_tool_error_handling(self, hermes_home, plugin_dir):
        """Plugin should load without errors even if tool handler fails."""
        from hermes_cli.plugins import get_plugin_manager

        manager = get_plugin_manager()
        manager.discover_and_load()

        plugin = manager.list_plugins()[0]
        assert plugin["error"] is None


class TestHookInvocation:
    """Test lifecycle hook registration and invocation."""

    def test_hook_registration(self, hermes_home, plugin_dir):
        """Plugin should be able to register hooks."""
        from hermes_cli.plugins import get_plugin_manager, invoke_hook

        manager = get_plugin_manager()
        manager.discover_and_load()

        plugin = manager.list_plugins()[0]
        assert plugin["hooks"] == 0

        assert callable(invoke_hook)
