# Weave Copilot Instructions

## Project Overview

Weave is a fully offline, on-device coding agent with local LLM inference via `llama-cpp-python`. It features a Textual-based TUI that's already functional—the UI is complete but many backend components are stub implementations waiting to be built.

**Current state**: The TUI scaffold (adapted from [Elia](https://github.com/darrenburns/elia)) works, but most modules in `src/weave/` contain only docstrings describing what to implement. Check if a module is a stub before assuming functionality exists.

## Architecture

```
src/weave/
├── tui/           # Working TUI (Textual) - entry point, screens, widgets
├── llm/           # LLM client - client.py has working llama.cpp streaming
├── agent/         # ReAct loop - mostly stubs (react.py, parser.py)
├── tools/         # Tool implementations - mostly stubs (file_ops.py, etc.)
├── sandbox/       # Code execution sandbox - stubs (validator.py, executor.py)
├── memory/        # Persistence layers - stubs (conversation.py, semantic.py)
├── chains/        # Workflow automation - stubs (loader.py, executor.py)
└── core/          # Config, registry, logging - stubs
```

**Key integration points** (where backend connects to TUI):
- `tui/widgets/chat.py::stream_agent_response()` → LLM streaming (currently placeholder)
- `tui/chats_manager.py` → In-memory storage (replace with SQLite for persistence)
- `tui/app.py::launch_chat()` → ReAct loop orchestration entry point

## Development Commands

```bash
# Run the app
python -m weave

# Run with Textual devtools (live CSS reload, DOM inspector)
textual run --dev -c "python -m weave"

# Install in development mode
pip install -e .

# Tests (note: test files contain only docstrings currently)
pytest tests/
```

## Code Patterns

### Textual TUI Patterns
- **Workers for async**: Use `@work(thread=True)` decorator for LLM inference to keep UI responsive. See `tui/widgets/chat.py::stream_agent_response()`.
- **Reactive attributes**: Use `reactive()` for UI state that should trigger updates. See `weave_theme` in `tui/app.py`.
- **Message passing**: Post Textual `Message` objects for widget communication. See `AgentResponseComplete` in `chat.py`.
- **Styling**: All CSS is in `tui/weave.scss`. Themes are in `tui/themes.py` using Pydantic models.

### LLM Integration
The working LLM client is in `llm/client.py`:
```python
from weave.llm.client import stream_chat_completion

for token in stream_chat_completion(messages):
    # Handle each token
```
Messages use OpenAI-compatible format: `{"role": "user|assistant|system", "content": "..."}`

### Tool Implementation Pattern
Tools should be sandboxed. When implementing:
1. Validate paths stay within working directory using `pathlib.Path.is_relative_to()`
2. Block dangerous operations via AST analysis before execution
3. Register tools in `core/registry.py` for LLM discovery

### Data Models
- `tui/models.py::ChatData` - Conversation container
- `tui/models.py::ChatMessage` - Individual message with role, content, timestamp
- `tui/models.py::MessageContent` - TypedDict for LLM-compatible message format

## Configuration

- User config: `~/.config/weave/config.toml` (XDG spec)
- User themes: `~/.config/weave/themes/*.yaml`
- Data storage: `~/.local/share/weave/` (intended, not yet implemented)
- Default config template: `config/default.toml` (currently empty)

## Testing Conventions

- Unit tests in `tests/unit/`, integration tests in `tests/integration/`
- Fixtures in `tests/fixtures/` (includes `malicious_code/` for sandbox testing)
- Test files exist but are stubs—implement tests alongside features

## What's Working vs Stubs

| Component | Status | Location |
|-----------|--------|----------|
| TUI (screens, widgets, themes) | ✅ Working | `tui/` |
| LLM streaming | ✅ Working | `llm/client.py` |
| Chat manager (in-memory) | ✅ Working | `tui/chats_manager.py` |
| ReAct loop | ❌ Stub | `agent/react.py` |
| Tool registry | ❌ Stub | `core/registry.py` |
| File operations | ❌ Stub | `tools/file_ops.py` |
| Sandbox validator | ❌ Stub | `sandbox/validator.py` |
| Persistence | ❌ Stub | `memory/conversation.py` |
| Chain executor | ❌ Stub | `chains/executor.py` |

## ReAct Loop Pattern (To Implement)

The agent should follow a Reason-Act-Observe loop in `agent/react.py`:
```python
while not done and iterations < MAX_ITERATIONS:
    response = llm.generate(conversation)
    if response.has_tool_call:
        result = registry.execute(tool_call)
        conversation.add_observation(result)
    else:
        done = True  # LLM responded to user
```

Key considerations:
- Maximum iteration limit (e.g., 10) to prevent infinite loops
- Loop detection: catch when same tool is called with identical args
- Error recovery: format tool errors for LLM to reason about alternatives
- Wire into `tui/app.py::launch_chat()` for orchestration

## Security: Sandbox Requirements

All code execution and file operations MUST be sandboxed. The `tests/fixtures/malicious_code/` directory contains attack vectors to test against.

**Path traversal prevention** (`tools/file_ops.py`):
```python
resolved = path.resolve()
if not resolved.is_relative_to(working_directory):
    raise PathTraversalError(f"Path escapes sandbox: {path}")
```

**AST-based code validation** (`sandbox/validator.py`):
- Block imports: `os`, `sys`, `subprocess`, `shutil`
- Block builtins: `open()`, `eval()`, `exec()`, `compile()`, `__import__()`
- Detect obfuscation: `getattr(os, 'system')`, `globals()['__builtins__']`

**Subprocess isolation** (`sandbox/executor.py`):
- Run validated code in separate process via `subprocess`
- Enforce timeouts to kill hanging processes
- Use `resource` module for CPU/memory limits (Linux)
- Capture stdout/stderr, never `shell=True`

## Key Files to Understand First

1. `tui/app.py` - Main app, screen navigation, system prompt
2. `tui/widgets/chat.py` - Core chat widget with streaming stub
3. `llm/client.py` - Working LLM integration example
4. `implementation.md` - Detailed build guide with phased approach
