"""
AST-based code validation.

Analyzes Python code before execution to block dangerous operations:
- Import statements (os, sys, subprocess, etc.)
- Built-in functions (open, eval, exec, compile)
- Attribute access patterns (__import__, getattr tricks)

Uses ast.NodeVisitor to walk the syntax tree.
"""

