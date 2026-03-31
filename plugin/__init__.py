"""Example Hermes plugin — register entry point.

This module is the entry point for the Hermes plugin system.
The `register(ctx)` function is called by the PluginManager
when the plugin is discovered and loaded.
"""

from .schemas import EXAMPLE_TOOL_SCHEMA
from .tools import example_tool_handler


def register(ctx):
    """Register all tools and hooks with the plugin context.

    Args:
        ctx: Plugin registration context provided by Hermes.
             Provides register_tool() and register_hook() methods.
    """
    # Register example tool
    ctx.register_tool(
        schema=EXAMPLE_TOOL_SCHEMA,
        handler=example_tool_handler,
    )

    # Example: register a lifecycle hook (commented out)
    # To add a hook, uncomment and provide a handler:
    #
    # def on_session_start(session, **kwargs):
    #     print(f"Session started: {session.id}")
    #
    # ctx.register_hook("on_session_start", on_session_start)
