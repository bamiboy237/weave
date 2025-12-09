"""
Tool call parsing from LLM output.

Extracts structured tool calls from LLM responses:
- JSON parsing with error recovery
- Tool name and argument extraction
- Malformed output handling
- Distinction between tool calls and final responses
"""
import json
import re
from typing import Optional

def parse_tool_call(llm_output: str) -> Optional[dict]:
    """
    Parse the LLM output to extract tool call information.

    Args:
        llm_output (str): The raw output string from the LLM.

    Returns:
        Optional[dict]: A dictionary with 'tool_name' and 'arguments' if a tool call is found, else None.
    """
    #  regex expression to find tool call patterns
    tool_call_pattern = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
    matches = tool_call_pattern.findall(llm_output)
    for match in matches:
        try:
            tool_call_json = json.load(match.strip())
            tool_name = tool_call_json