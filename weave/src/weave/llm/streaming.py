"""
Streaming generation handler.

Implements token-by-token streaming from the LLM:
- Generator-based API for memory efficiency
- Cancellation support mid-generation
- Integration with async event loop
- Callback hooks for UI updates
"""

