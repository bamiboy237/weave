"""
Core Reason-Act-Observe loop.

The main agent loop that:
1. Receives user input
2. LLM reasons about what to do
3. LLM calls tools if needed
4. Observes tool results
5. Continues reasoning or returns final response

Includes iteration limits and loop detection.
"""

