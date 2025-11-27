"""
Whitelisted shell command tool.

Allows execution of specific shell commands:
- Configurable command whitelist (git, ls, grep, etc.)
- Argument validation to prevent injection
- Output capture and size limiting
- Never uses shell=True

Security-focused design blocks non-whitelisted commands.
"""

