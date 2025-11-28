"""
Tool call parsing from LLM output.

Extracts structured tool calls from LLM responses:
- JSON parsing with error recovery
- Tool name and argument extraction
- Malformed output handling
- Distinction between tool calls and final responses
"""

