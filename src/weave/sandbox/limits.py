"""
Resource limit configuration.

Applies OS-level resource limits to sandboxed code:
- CPU time limits (RLIMIT_CPU)
- Memory limits (RLIMIT_AS)
- Process limits (RLIMIT_NPROC) for fork bomb protection
- File descriptor limits

Note: Some limits are platform-specific (Linux vs macOS).
"""

