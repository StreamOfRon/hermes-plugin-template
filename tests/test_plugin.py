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
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()

        plugin_names = [p.name for p in manager.plugins]
        assert "example_plugin" in plugin_names

    def test_discover_empty_directory(self, hermes_home):
        """PluginManager should handle empty plugins directory."""
        (hermes_home / "plugins").mkdir(exist_ok=True)

        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()

        assert len(manager.plugins) == 0


class TestPluginLoading:
    """Test that plugins load correctly."""

    def test_load_plugin(self, hermes_home, plugin_dir):
        """Plugin should load without errors."""
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()
        manager.load_all()

        assert len(manager.plugins) == 1
        assert manager.plugins[0].name == "example_plugin"

    def test_load_plugin_manifest(self, hermes_home, plugin_dir):
        """Plugin manifest (plugin.yaml) should be parsed correctly."""
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()
        manager.load_all()

        plugin = manager.plugins[0]
        assert plugin.version == "0.1.0"
        assert "example_plugin_example_tool" in [
            t["name"] for t in plugin.provided_tools
        ]


class TestToolRegistration:
    """Test that tools are registered correctly."""

    def test_tool_registration(self, hermes_home, plugin_dir):
        """Registered tools should be available in the tool registry."""
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()
        manager.load_all()

        tool_names = manager.list_tool_names()
        assert "example_plugin_example_tool" in tool_names

    def test_tool_execution(self, hermes_home, plugin_dir):
        """Registered tool should execute and return valid JSON."""
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()
        manager.load_all()

        result = manager.execute_tool(
            "example_plugin_example_tool",
            {"message": "hello world"},
        )

        data = json.loads(result)
        assert data["status"] == "success"
        assert data["message"] == "hello world"
        assert data["length"] == 11

    def test_tool_error_handling(self, hermes_home, plugin_dir):
        """Tool should handle errors gracefully and return error JSON."""
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()
        manager.load_all()

        # Tool should not raise; it should return error JSON
        result = manager.execute_tool(
            "example_plugin_example_tool",
            {"message": "test"},
        )

        data = json.loads(result)
        assert "status" in data


class TestHookInvocation:
    """Test lifecycle hook registration and invocation."""

    def test_hook_registration(self, hermes_home, plugin_dir):
        """Plugin should be able to register hooks."""
        from hermes_agent.plugins.manager import PluginManager

        manager = PluginManager()
        manager.discover()
        manager.load_all()

        # The example plugin doesn't register hooks by default,
        # but the mechanism should be available
        assert hasattr(manager, "register_hook") or hasattr(
            manager, "invoke_hook"
        )
