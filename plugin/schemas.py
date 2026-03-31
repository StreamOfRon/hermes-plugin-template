"""Tool schema definitions for the example plugin.

Each schema follows the OpenAI function-calling format.
The schema name must match the plugin.yaml provides_tools entry.
"""

EXAMPLE_TOOL_SCHEMA = {
    "name": "example_plugin_example_tool",
    "description": "An example tool that demonstrates the Hermes plugin tool contract",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "A message to process",
            },
            "verbose": {
                "type": "boolean",
                "description": "Whether to return verbose output",
                "default": False,
            },
        },
        "required": ["message"],
    },
}
