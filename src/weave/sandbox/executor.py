"""
Subprocess execution.

Runs validated code in an isolated subprocess:
- Separate process for memory isolation
- stdout/stderr capture
- Timeout enforcement with process termination
- Crash isolation from main application
"""

