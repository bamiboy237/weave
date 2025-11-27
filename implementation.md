# Building Weave: An On-Device Coding Agent

> **The Learning Philosophy**  
> This guide will never show you code. It will tell you *what* to build, *why* it matters, and point you to the resources to figure out *how*. The struggle with documentation is where real learning happens. If you copy-paste solutions, you'll have a working agent but no understanding. If you fight through the docs, you'll have both.

---

## What You're Building

**Weave** is a fully offline coding agent that runs on your machine. No API calls, no data leaving your computer, no subscription fees. By the end of this guide, you'll have built:

- A local LLM inference engine that streams responses
- A terminal UI that stays responsive during generation
- A tool system the agent uses to read files, execute code, and search
- A memory system that persists across sessions
- Tool chains that automate multi-step workflows
- A code execution sandbox that won't let the agent destroy your system

---

## How This Guide Works

Each step follows this pattern:

1. **What** — The problem you're solving
2. **Why** — Why this matters for the system
3. **Do Now** — Specific actions to take
4. **Success Criteria** — How you know you're done
5. **Resources** — Documentation to study
6. **Thinking Prompts** — Questions to wrestle with
7. **Milestone** — What you have when you finish

**The steps are sequential.** Each builds on the previous. Don't skip ahead — if you're stuck on Step 3, you're not ready for Step 4.

---

## Phase 0: Environment & Foundations

Before you write agent code, you need a working environment and must understand the core technologies. This phase sets up your project and builds curses intuition.

---

### Step 0.1: Environment Setup

#### What
Create a Python virtual environment and verify you have the right Python version.

#### Why
You need Python 3.11+ (for `tomllib` and other features). A virtual environment isolates dependencies so you don't pollute your system Python.

#### Do Now
1. Check your Python version: `python3 --version` (must be 3.11+)
2. If not 3.11+, install it via pyenv, homebrew, or your OS package manager
3. Create a project directory: `mkdir weave && cd weave`
4. Create a virtual environment: `python3 -m venv .venv`
5. Activate it: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
6. Verify: `which python` should point to your `.venv`

#### Success Criteria
- [ ] `python --version` shows 3.11 or higher
- [ ] `which python` points to `.venv/bin/python`
- [ ] You can run `python -c "import tomllib; print('ok')"` without error

#### Resources
- [pyenv](https://github.com/pyenv/pyenv) — If you need to install Python 3.11+
- [venv documentation](https://docs.python.org/3/library/venv.html)

#### Milestone
You have an isolated Python 3.11+ environment ready for development.

---

### Step 0.2: Project Structure

#### What
Create a Python package structure that can be run as a module (`python -m weave`).

#### Why
A coding agent has many moving parts: LLM client, tools, memory, UI. If these are tangled together, you can't test or modify one without breaking others. Good structure prevents future pain.

#### Do Now
1. Create the src-layout directory structure:
   - `src/weave/` — The main package
   - `src/weave/core/` — Configuration, logging, registry, exceptions
   - `src/weave/llm/` — LLM client, streaming, chat formatting
   - `src/weave/agent/` — ReAct loop, prompts, parsing
   - `src/weave/tools/` — File ops, HTTP, shell, scraper
   - `src/weave/sandbox/` — Code validation and execution
   - `src/weave/memory/` — Conversation, project context, semantic search
   - `src/weave/chains/` — Tool chain loader and executor
   - `src/weave/tui/` — Terminal UI components
   - `tests/` — Test files
2. Create `__init__.py` files in each directory
3. Create `src/weave/__main__.py` — This makes `python -m weave` work
4. Create `pyproject.toml` at the project root — Define project metadata and dependencies

#### Success Criteria
- [ ] `pip install -e .` installs your package in development mode
- [ ] `python -m weave` runs (even if it just prints "Hello" for now)
- [ ] `from weave.core import config` works without errors
- [ ] No circular import errors

#### Resources
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [PEP 518: pyproject.toml](https://peps.python.org/pep-0518/)
- [`__main__.py` explained](https://docs.python.org/3/library/__main__.html)
- [src-layout vs flat-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

#### Thinking Prompts
1. Why does `src/weave/` exist inside the project, not just `weave/`?
2. How do you prevent `weave.core` from accidentally depending on `weave.tui`?
3. What happens if two modules try to import each other?

#### Milestone
Running `python -m weave` launches your application (even if it does nothing yet).

---

### Step 0.3: Curses Fundamentals

#### What
Build a simple curses application that displays scrollable text and handles keyboard input. **This is a throwaway learning exercise** — the code doesn't need to be perfect.

#### Why
Curses is the foundation of your entire UI. If you don't understand it deeply now, you'll spend hours debugging mysterious screen corruption later. This step builds intuition.

#### Do Now
1. **First, read** the Curses Programming HOWTO completely
2. Create a test file `experiments/curses_test.py` (outside your main package)
3. Build a simple app that:
   - Takes over the terminal
   - Displays some text
   - Scrolls with arrow keys
   - Exits cleanly on 'q'
4. Break it intentionally (exit without cleanup, write past window edge) to see what happens
5. Add colors

#### Success Criteria
- [ ] Application takes over the terminal (alternate screen buffer)
- [ ] Text can be scrolled up/down with arrow keys
- [ ] Window resizes don't crash the application
- [ ] Pressing 'q' exits cleanly — terminal returns to normal
- [ ] At least 8 colors work

#### Resources
- [Curses Programming HOWTO](https://docs.python.org/3/howto/curses.html) — **Start here, read it all**
- [Python curses module](https://docs.python.org/3/library/curses.html) — Reference documentation
- [ncurses man pages](https://invisible-island.net/ncurses/man/ncurses.3x.html) — Explains concepts Python assumes you know

#### Thinking Prompts
1. What's the difference between `stdscr`, a `window`, and a `pad`?
2. What happens if you write a character past the edge of a window?
3. Why does `curses.wrapper()` exist? What problem does it solve?
4. If your program crashes without calling `endwin()`, what happens to the terminal?

#### Milestone
You have a working curses application you can run, resize, scroll, and exit cleanly.

---

### Step 0.4: Async + Curses Integration

#### What
Make curses work with asyncio so the UI stays responsive during long operations.

#### Why
LLM inference takes 10-30 seconds. If your UI blocks during generation, users stare at a frozen screen. They can't cancel, can't scroll, can't do anything. You need async.

The challenge: `getch()` blocks by default. Asyncio's event loop can't run while waiting for input.

#### Do Now
1. **First, read** about curses' `nodelay()` and `timeout()` modes
2. **Then read** asyncio basics (coroutines, event loop, tasks)
3. Modify your curses test to:
   - Run a background task (use `asyncio.sleep(5)` to simulate work)
   - Update a "status" area while the task runs
   - Allow keyboard input during the task
   - Cancel the task if user presses Escape
4. Test: Can you type while the background task is "working"?

#### Success Criteria
- [ ] UI updates while a background task runs
- [ ] User can type while the "agent" is "thinking"
- [ ] No race conditions when multiple coroutines update the screen
- [ ] Ctrl+C or Escape cancels the current operation cleanly

#### Resources
- [asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [asyncio event loops](https://docs.python.org/3/library/asyncio-eventloop.html)
- Search: "curses nodelay mode"
- Search: "curses timeout"
- Search: "asyncio run_in_executor"

#### Thinking Prompts
1. How do you make `getch()` non-blocking? What's the tradeoff?
2. If you use `asyncio.run()`, where does the curses main loop go?
3. What happens if two coroutines try to write to the screen at the same time?

#### Milestone
You have an async curses application that can run background tasks while staying responsive to input.

---

## Phase 1: Local LLM Integration

Now you'll add the brain. This phase connects your application to a local language model.

---

### Step 1.1: Download a Model

#### What
Download a quantized language model that will run on your hardware.

#### Why
Local inference requires a model file on your disk. Different quantization levels trade quality for memory/speed. You need to choose based on your hardware.

#### Do Now
1. **Check your hardware:**
   - How much RAM do you have? (16GB minimum recommended)
   - Do you have a GPU? What VRAM? (optional but faster)
2. **Choose a model:**
   - For 16GB RAM: Qwen2.5-Coder-7B-Instruct-Q4_K_M (~5GB)
   - For 32GB+ RAM: Qwen2.5-Coder-7B-Instruct-Q8_0 (~8GB) or 14B variant
3. **Download from Hugging Face:**
   - Go to [Qwen2.5-Coder GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF)
   - Download the `.gguf` file matching your choice
   - Save it somewhere accessible (e.g., `~/.local/share/weave/models/` or `./models/`)
4. **Note the full path** — you'll need it in the next step

#### Success Criteria
- [ ] You have a `.gguf` file on disk
- [ ] You can explain why you chose that quantization level
- [ ] You know the file's full path

#### Resources
- [Qwen2.5-Coder on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF)
- Search: "GGUF format explained"
- Search: "Q4_K_M vs Q8_0 quantization comparison"
- [llama.cpp quantization types](https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/quantize.cpp)

#### Thinking Prompts
1. What does Q4_K_M mean? How is it different from Q4_0 or Q8_0?
2. Why would a smaller quantization be faster but less accurate?
3. How much RAM do you expect this model to use?

#### Milestone
You have a model file on disk, ready to load.

---

### Step 1.2: Install llama-cpp-python

#### What
Install the `llama-cpp-python` library that will load and run your model.

#### Why
`llama-cpp-python` is a Python binding for llama.cpp, the engine that runs GGUF models locally. Installation can be tricky because it needs to compile native code.

#### Do Now
1. **Install build dependencies** (if on macOS/Linux, you likely have them; Windows needs Visual Studio Build Tools)
2. **Decide on GPU support:**
   - For CPU only: `pip install llama-cpp-python`
   - For Apple Metal: `CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python`
   - For NVIDIA CUDA: `CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python`
3. **Add to your pyproject.toml** dependencies
4. **Test the installation:** Import it in Python and ensure no errors

#### Success Criteria
- [ ] `from llama_cpp import Llama` works without error
- [ ] If using GPU, verify it's detected (check the library's debug output)
- [ ] The library is listed in your pyproject.toml dependencies

#### Resources
- [llama-cpp-python documentation](https://llama-cpp-python.readthedocs.io/)
- [llama-cpp-python GitHub](https://github.com/abetlen/llama-cpp-python)
- [Installation instructions](https://github.com/abetlen/llama-cpp-python#installation)

#### Thinking Prompts
1. Why does this library need to compile native code?
2. What's the difference between CPU, Metal, and CUDA backends?
3. If installation fails, how would you debug it?

#### Milestone
llama-cpp-python is installed and importable.

---

### Step 1.3: Load the Model

#### What
Load your downloaded model into memory and generate a simple response.

#### Why
This verifies your model file works and you understand the basic API. If loading fails, you need to debug before building more.

#### Do Now
1. Create `src/weave/llm/client.py`
2. Write code that:
   - Loads the model from your downloaded file path
   - Configures `n_ctx` (context window size) — start with 4096
   - Configures `n_gpu_layers` (if using GPU) — start with 0, then experiment
   - Generates a simple completion for "Hello, my name is"
3. Run it and observe:
   - How long does loading take?
   - How much RAM does it use? (check Activity Monitor / htop)
   - What does the output look like?

#### Success Criteria
- [ ] Model loads without crashing
- [ ] A simple prompt returns a coherent response
- [ ] You can explain what `n_ctx` and `n_gpu_layers` do
- [ ] If using GPU, you see GPU memory being used

#### Resources
- [llama-cpp-python documentation](https://llama-cpp-python.readthedocs.io/)
- [llama.cpp README](https://github.com/ggerganov/llama.cpp) — Explains the underlying concepts
- Search: "llama-cpp-python n_gpu_layers"

#### Thinking Prompts
1. What does `n_ctx` control? What happens if you set it too high?
2. What is `n_gpu_layers`? How do you choose the right value?
3. Why might generation be fast at first then slow down mid-response?
4. What happens if the model file path is wrong?

#### Milestone
You can load a model and generate text completions.

---

### Step 1.4: Streaming Generation

#### What
Implement token-by-token streaming so users see output as it's generated.

#### Why
A 20-second generation that streams tokens feels faster than a 15-second generation that appears all at once. Users can also cancel mid-generation if the response is wrong.

#### Do Now
1. Modify your client to use the streaming API
2. Implement a generator that yields tokens as they're produced
3. Write a test that:
   - Starts generation
   - Prints each token as it arrives
   - Can be cancelled mid-stream (e.g., after 10 tokens)
4. Hook this into your async curses application from Phase 0

#### Success Criteria
- [ ] Tokens appear one-by-one as the model generates
- [ ] UI updates smoothly during generation
- [ ] Generation can be cancelled mid-stream
- [ ] You're using the streaming API, not generating all at once

#### Resources
- llama-cpp-python: Look for `stream=True` in the documentation
- Search: "llama-cpp-python streaming"
- [Python generators](https://realpython.com/introduction-to-python-generators/)

#### Thinking Prompts
1. What is a Python generator? How is `yield` different from `return`?
2. If generation is running in a loop, how do you check for cancellation?
3. How do you update the curses display from within a generator loop?

#### Milestone
Your application streams LLM output token-by-token to the screen.

---

### Step 1.5: Chat Completion Format

#### What
Format conversations properly so the model responds as an assistant, not just completing arbitrary text.

#### Why
Raw text completion isn't a conversation. If you just send "What's 2+2?", the model might continue your text instead of answering. Chat formats tell the model who's speaking.

#### Do Now
1. **First, read** about your model's chat template (find it on the Hugging Face model card)
2. Create `src/weave/llm/chat.py`
3. Implement message formatting that:
   - Takes a list of messages (system, user, assistant)
   - Formats them using the correct chat template
   - Returns a properly formatted string for the model
4. Test multi-turn conversations:
   - Send "What's 2+2?"
   - Get response
   - Send "What's that plus 10?"
   - Does it remember the context?

#### Success Criteria
- [ ] You can send conversation history, not just single prompts
- [ ] Model responds as an "assistant," not continuing your text
- [ ] System prompts are respected
- [ ] Multi-turn conversations maintain coherence

#### Resources
- [Qwen2.5-Coder model card](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) — Find the chat template
- Search: "ChatML format"
- Search: "llama-cpp-python chat completion"
- llama-cpp-python: Look for `create_chat_completion`

#### Thinking Prompts
1. What's a "chat template"? Why do different models need different ones?
2. What happens if you use the wrong template?
3. Where does the system prompt go in the conversation structure?

#### Milestone
You can have multi-turn conversations with the LLM in your curses UI.

---

## Phase 2: Tool System

An LLM that can only talk is useless for coding. This phase gives your agent the ability to interact with files and the system.

---

### Step 2.1: Tool Schema Design

#### What
Design a schema format that describes tools: what they do, what inputs they need, what outputs they produce.

#### Why
The LLM needs to know what tools exist and how to use them. A well-designed schema serves as documentation for the LLM AND validates arguments before execution.

#### Do Now
1. **First, read** the OpenAI function calling format (it's the industry standard)
2. **Then read** JSON Schema basics
3. Create `src/weave/tools/schema.py`
4. Design your schema format — decide:
   - What fields every tool schema must have (name, description, parameters, etc.)
   - How to represent required vs optional parameters
   - How to represent parameter types (string, integer, enum, etc.)
5. Write example schemas for a hypothetical `read_file` tool and `list_directory` tool

#### Success Criteria
- [ ] Schemas can be serialized to JSON
- [ ] Schema includes: name, description, parameters (with types), required fields
- [ ] A human reading the schema understands what the tool does
- [ ] You have schemas for at least 2 example tools

#### Resources
- [JSON Schema specification](https://json-schema.org/understanding-json-schema/)
- [OpenAI function calling format](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic tool use format](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

#### Thinking Prompts
1. How do you represent optional vs. required parameters?
2. How do you represent enums (parameter must be one of specific values)?
3. Should schemas be defined in code or config files?

#### Milestone
You have a schema format and example schemas for file tools.

---

### Step 2.2: Tool Registry

#### What
Create a central registry where tools register themselves. The registry provides schemas to the LLM and dispatches execution.

#### Why
You don't want to manually maintain a list of tools. New tools should "plug in" without modifying core code.

#### Do Now
1. Create `src/weave/core/registry.py`
2. Implement a registry that:
   - Allows tools to register via a decorator
   - Collects all registered tool schemas
   - Dispatches `execute("tool_name", {args})` to the correct tool
   - Raises clear errors for unknown tools
3. Write a simple test tool that just returns its arguments

#### Success Criteria
- [ ] Tools can register without modifying registry code
- [ ] `registry.get_all_schemas()` returns all tool schemas
- [ ] `registry.execute("tool_name", {args})` works
- [ ] Unknown tool names raise clear errors

#### Resources
- [Python decorators guide](https://realpython.com/primer-on-python-decorators/)
- Search: "registry pattern Python"
- Search: "plugin architecture Python"

#### Thinking Prompts
1. How can a decorator register a function with a central registry?
2. Should tools be classes or functions? What's the tradeoff?
3. If tools are in separate files, how do they get registered at startup?

#### Milestone
You have a working registry and can register/execute tools.

---

### Step 2.3: File Operation Tools

#### What
Build the essential file tools: read, write, list directory, search. These MUST be sandboxed.

#### Why
File operations are the most common thing an agent does. But they're dangerous — an agent that can read `~/.ssh/id_rsa` is a security nightmare.

#### Do Now
1. Install no new dependencies — use Python's built-in `pathlib`
2. Create `src/weave/tools/file_ops.py`
3. Implement tools:
   - `read_file(path)` — Returns file contents
   - `write_file(path, content)` — Creates or overwrites
   - `list_directory(path)` — Lists contents
   - `search_files(pattern, path)` — Finds text in files
4. **Implement sandboxing:**
   - All paths must resolve within a "working directory"
   - Block `../../../etc/passwd` style attacks
   - Handle symlinks pointing outside sandbox
5. Write tests for the sandbox (try to escape it!)

#### Success Criteria
- [ ] All four tools work correctly
- [ ] Paths are resolved relative to working directory
- [ ] `../../../etc/passwd` fails safely
- [ ] Symlinks pointing outside are blocked

#### Resources
- [pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Path.resolve() and Path.is_relative_to()](https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.is_relative_to)
- Search: "path traversal attack prevention Python"

#### Thinking Prompts
1. How do you ensure a path stays within a directory after resolution?
2. What's the difference between `resolve()` and `absolute()`?
3. What encoding should you use when reading files?

#### Milestone
You have working, sandboxed file tools registered in your registry.

---

### Step 2.4: LLM Tool Calling Integration

#### What
Make the LLM actually call your tools. When asked "What's in main.py?", it should output a structured tool call.

#### Why
This is where it all comes together. The LLM sees tool schemas, decides to use a tool, outputs a structured call, you execute it, feed results back.

#### Do Now
1. Create `src/weave/agent/parser.py`
2. Modify your system prompt to:
   - Include all tool schemas
   - Instruct the LLM to output tool calls in a specific format (JSON)
3. Implement parsing to extract tool calls from LLM output
4. Test the full flow:
   - User asks "What files are in this directory?"
   - LLM outputs a `list_directory` tool call
   - You parse and execute it
   - You send results back to LLM
   - LLM responds to user

#### Success Criteria
- [ ] LLM receives tool schemas in its context
- [ ] When asked about files, LLM outputs a tool call
- [ ] You can parse the tool call from LLM output
- [ ] Tool results are sent back and incorporated

#### Resources
- Search: "llama.cpp function calling"
- Search: "local LLM tool calling"
- [Outlines library](https://github.com/outlines-dev/outlines) — Grammar-constrained generation (optional)

#### Thinking Prompts
1. How do you instruct the LLM to output JSON instead of prose?
2. What if the LLM outputs malformed JSON? How do you recover?
3. How do you distinguish "LLM wants a tool" from "LLM is done"?

#### Milestone
Your agent can answer questions by calling tools and reasoning about results.

---

## Phase 3: The ReAct Loop

Your agent can think and act once. Now teach it to chain actions for complex tasks.

---

### Step 3.1: The Core Loop

#### What
Implement the Reason-Act-Observe loop for multi-step task completion.

#### Why
Real tasks aren't one-shot. "Fix the bug" requires: read code → understand → identify fix → write fix → test → iterate. ReAct enables this.

#### Do Now
1. **First, read** the ReAct paper abstract and examples
2. Create `src/weave/agent/react.py`
3. Implement the loop:
   ```
   while not done:
       response = llm.generate(conversation)
       if response.has_tool_call:
           result = registry.execute(tool_call)
           conversation.add_observation(result)
       else:
           done = True  # LLM responded to user
   ```
4. Add safeguards:
   - Maximum iteration limit (e.g., 10)
   - Loop detection (calling same tool with same args)
5. Test with a multi-step task: "Read main.py and tell me what functions it defines"

#### Success Criteria
- [ ] Agent completes tasks requiring 3+ tool calls
- [ ] Each iteration: reason → act → observe
- [ ] Agent knows when to stop
- [ ] Conversation history is maintained across iterations

#### Resources
- [ReAct paper](https://arxiv.org/abs/2210.03629)
- [Siddharth Bharath's coding agent tutorial](https://www.siddharthbharath.com/build-a-coding-agent-python-tutorial/)

#### Thinking Prompts
1. How does the LLM signal "I'm done" vs "I need another tool"?
2. What's the maximum iteration limit? Why?
3. How do you detect infinite loops?

#### Milestone
Your agent can complete multi-step tasks autonomously.

---

### Step 3.2: Error Handling & Recovery

#### What
Handle tool failures gracefully. The agent should adapt, not crash.

#### Why
Things fail. Files don't exist. Paths are wrong. An agent that crashes on errors is useless. An agent that reasons about errors is powerful.

#### Do Now
1. Create `src/weave/core/exceptions.py` with custom exceptions
2. Modify tools to raise typed exceptions (FileNotFoundError, PathTraversalError, etc.)
3. Modify the ReAct loop to:
   - Catch tool errors
   - Format them for the LLM
   - Let the LLM reason and try alternatives
4. Test: Ask the agent to read a file that doesn't exist. Does it recover?

#### Success Criteria
- [ ] Tool errors are reported to the LLM, not swallowed
- [ ] LLM can reason about errors and try alternatives
- [ ] User sees what went wrong
- [ ] Critical errors exit gracefully

#### Resources
- [Python exception handling](https://docs.python.org/3/tutorial/errors.html)
- [Custom exceptions](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)

#### Thinking Prompts
1. Should tool errors be exceptions or return values?
2. How do you format errors so the LLM understands them?
3. If the LLM makes the same mistake 3 times, should you intervene?

#### Milestone
Your agent handles errors gracefully and can recover from failures.

---

### Step 3.3: Context Window Management

#### What
Handle the limited context window. Long conversations must be truncated intelligently.

#### Why
Your model has 4K-8K tokens. Long conversations exceed this. You need intelligent truncation without losing critical information.

#### Do Now
1. Create `src/weave/llm/context.py`
2. Implement token counting for your model's tokenizer
3. Implement a context management strategy:
   - Always keep: system prompt, current task, recent messages
   - Truncate or summarize: old conversation turns
4. Test: Have a conversation longer than your context window. Does it still work?

#### Success Criteria
- [ ] Agent handles conversations longer than context window
- [ ] Old messages are summarized or truncated
- [ ] Critical info (current task, recent results) is preserved
- [ ] Agent doesn't forget mid-task

#### Resources
- [tiktoken](https://github.com/openai/tiktoken) — Or find your model's tokenizer
- Search: "context window management LLM"
- llama-cpp-python: Look for tokenizer methods

#### Thinking Prompts
1. How do you count tokens for your specific model?
2. When context is full, what do you drop? What do you keep?
3. Should summarization use the same LLM?

#### Milestone
Your agent can handle arbitrarily long conversations without breaking.

---

## Phase 4: Memory System

The agent should remember across sessions. This phase adds persistent memory.

---

### Step 4.1: Conversation Persistence (Tier 1)

#### What
Save and restore conversation history so sessions survive restarts.

#### Why
Closing the app shouldn't mean losing context. Users want to continue where they left off.

#### Do Now
1. Create `src/weave/memory/conversation.py`
2. Implement:
   - Save conversation to JSON file
   - Load conversation on startup
   - Multiple session support (create, switch, list, delete)
3. Decide where to store files (XDG spec recommends `~/.local/share/weave/`)
4. Handle corrupted files gracefully

#### Success Criteria
- [ ] Closing and reopening restores the conversation
- [ ] Multiple sessions can be saved and switched
- [ ] Old sessions can be deleted
- [ ] Corrupted files don't crash the app

#### Resources
- [json module](https://docs.python.org/3/library/json.html)
- Search: "XDG base directory specification"
- [pickle](https://docs.python.org/3/library/pickle.html) — And why NOT to use it

#### Thinking Prompts
1. JSON can't serialize everything. What types might fail?
2. How do you handle corrupted history files?
3. What metadata should be saved alongside conversation?

#### Milestone
Conversations persist across application restarts.

---

### Step 4.2: Project Context (Tier 2)

#### What
Store project-specific data in SQLite: file caches, symbol indices.

#### Why
Re-reading every file is slow. Caching and indexing makes the agent faster and more aware.

#### Do Now
1. **Install sqlite3** — It's built into Python
2. Create `src/weave/memory/project.py`
3. Design a schema for:
   - File cache (path, content, hash, last_indexed)
   - Symbol index (name, type, file, line_number)
4. Implement:
   - Create database on first use
   - Detect file changes via hash
   - Index Python files for functions/classes

#### Success Criteria
- [ ] Each project directory gets its own database
- [ ] File hashes detect changes
- [ ] Symbol index stores function/class locations
- [ ] Database is created automatically

#### Resources
- [sqlite3 module](https://docs.python.org/3/library/sqlite3.html)
- Search: "SQLite schema design"
- Search: "Python AST extract functions classes"

#### Thinking Prompts
1. How do you detect if a file changed since indexing?
2. What happens if the schema needs to change later?
3. Should database access be sync or async?

#### Milestone
Your agent has cached knowledge about the project structure.

---

### Step 4.3: Semantic Search (Tier 3)

#### What
Implement vector-based semantic search over conversations and code.

#### Why
"Find where we discussed authentication" requires semantic understanding, not keyword matching.

#### Do Now
1. **Install dependencies:**
   - `pip install chromadb sentence-transformers`
   - Add to pyproject.toml
2. Create `src/weave/memory/semantic.py`
3. Implement:
   - Embed text into vectors
   - Store and retrieve from ChromaDB
   - Search by similarity
4. Index past conversations and code snippets
5. Test: "Find conversations about file handling" — do relevant results come up?

#### Success Criteria
- [ ] Text can be embedded into vectors
- [ ] Similar queries return similar results
- [ ] Search is fast (sub-second)
- [ ] ChromaDB persists to disk

#### Resources
- [ChromaDB documentation](https://docs.trychroma.com/)
- [sentence-transformers](https://www.sbert.net/)
- Search: "vector embeddings explained"

#### Thinking Prompts
1. What is an embedding? How does it capture "meaning"?
2. How do you choose chunk size for code files?
3. How do you keep the index in sync with changing files?

#### Milestone
Your agent can semantically search past conversations and code.

---

## Phase 5: Code Execution Sandbox

Your agent needs to run code safely. This phase builds security.

---

### Step 5.1: AST-Based Validation

#### What
Analyze code statically before execution. Block dangerous operations at the syntax level.

#### Why
LLM-generated code can't be trusted. Static analysis catches many dangerous patterns.

#### Do Now
1. Create `src/weave/sandbox/validator.py`
2. Implement an `ast.NodeVisitor` that blocks:
   - `import os`, `import sys`, `import subprocess`
   - `open()`, `eval()`, `exec()`, `compile()`
   - `__import__()`, dangerous `getattr()` patterns
3. Return clear error messages explaining WHY code was blocked
4. Write tests with known-dangerous code snippets

#### Success Criteria
- [ ] `import os` is blocked
- [ ] `open()` is blocked
- [ ] `eval()` and `exec()` are blocked
- [ ] Safe code (print, math) passes
- [ ] Errors explain why code was blocked

#### Resources
- [ast module](https://docs.python.org/3/library/ast.html)
- [ast.NodeVisitor](https://docs.python.org/3/library/ast.html#ast.NodeVisitor)
- [Green Tree Snakes AST tutorial](https://greentreesnakes.readthedocs.io/)

#### Thinking Prompts
1. What's the difference between `ast.parse()` and `compile()`?
2. Can you detect `__import__()` or `getattr(os, 'system')`?
3. What can slip through static analysis?

#### Milestone
You have a validator that blocks dangerous code patterns.

---

### Step 5.2: Subprocess Sandboxing

#### What
Run validated code in a separate subprocess.

#### Why
Even validated code can crash, hang, or consume memory. Subprocess isolation prevents these from killing your app.

#### Do Now
1. Create `src/weave/sandbox/executor.py`
2. Implement execution that:
   - Runs code in a subprocess
   - Captures stdout/stderr
   - Enforces a timeout
   - Kills the process if it hangs
3. Test with infinite loops and crash-inducing code

#### Success Criteria
- [ ] Code runs in a separate process
- [ ] stdout and stderr are captured
- [ ] Execution times out after N seconds
- [ ] Infinite loops don't hang the app
- [ ] Crashes don't crash the main app

#### Resources
- [subprocess module](https://docs.python.org/3/library/subprocess.html)
- [asyncio.create_subprocess_exec()](https://docs.python.org/3/library/asyncio-subprocess.html)
- Search: "Python subprocess timeout"

#### Thinking Prompts
1. What's the difference between `run()` and `Popen()`?
2. How do you kill a process that won't stop?
3. What if the subprocess forks a child?

#### Milestone
Code executes in an isolated, time-limited subprocess.

---

### Step 5.3: Resource Limits

#### What
Apply OS-level limits on CPU time, memory, and processes.

#### Why
A subprocess can still monopolize resources. Limits prevent memory bombs and fork bombs.

#### Do Now
1. Create `src/weave/sandbox/limits.py`
2. Implement limits using the `resource` module:
   - CPU time limit
   - Memory limit
   - Process limit (prevent fork bombs)
3. Test with memory-allocating and CPU-intensive code
4. Note: Some limits work differently on macOS vs Linux

#### Success Criteria
- [ ] Infinite loops are killed after N CPU seconds
- [ ] Memory bombs are killed
- [ ] Fork bombs are prevented
- [ ] Violations produce clear errors

#### Resources
- [resource module](https://docs.python.org/3/library/resource.html)
- Search: "rlimit Python"
- Note: macOS has different limit support than Linux

#### Thinking Prompts
1. What's the difference between wall-clock time and CPU time?
2. How do you set limits for a subprocess?
3. What signal is sent when limits are exceeded?

#### Milestone
Code execution has hard resource limits.

---

## Phase 6: Additional Tools

Expand the agent's capabilities.

---

### Step 6.1: HTTP Request Tool

#### What
A tool that makes HTTP requests to fetch docs, call APIs, etc.

#### Why
The agent can't be truly helpful in isolation. But HTTP needs security controls.

#### Do Now
1. **Install httpx:** `pip install httpx` and add to pyproject.toml
2. Create `src/weave/tools/http.py`
3. Implement a tool with:
   - GET and POST support
   - Custom headers
   - JSON parsing
   - Configurable timeout
   - Domain whitelist

#### Success Criteria
- [ ] GET and POST work
- [ ] JSON responses are parsed
- [ ] Timeouts prevent hanging
- [ ] Only whitelisted domains are allowed

#### Resources
- [httpx documentation](https://www.python-httpx.org/)
- Search: "HTTP request security"

#### Milestone
Your agent can make controlled HTTP requests.

---

### Step 6.2: Web Scraper Tool

#### What
Extract readable content from web pages.

#### Why
Web pages are 90% boilerplate. The LLM needs clean content.

#### Do Now
1. **Install BeautifulSoup:** `pip install beautifulsoup4` and add to pyproject.toml
2. Create `src/weave/tools/scraper.py`
3. Implement scraping that:
   - Fetches the page (reuse your HTTP tool)
   - Extracts main content
   - Returns plain text or markdown
   - Truncates large pages

#### Success Criteria
- [ ] HTML is parsed
- [ ] Main content is extracted
- [ ] Result is readable text
- [ ] Large pages are truncated

#### Resources
- [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- Search: "readability algorithm"

#### Milestone
Your agent can read web pages.

---

### Step 6.3: Shell Command Tool (Whitelisted)

#### What
Allow specific shell commands (git, ls, grep) without full shell access.

#### Why
Shell access is powerful but dangerous. Whitelist makes it controlled.

#### Do Now
1. Create `src/weave/tools/shell.py`
2. Implement with:
   - A configurable whitelist of allowed commands
   - Argument validation (prevent injection)
   - **Never use `shell=True`**
   - Output capture and size limiting

#### Success Criteria
- [ ] Whitelisted commands work
- [ ] Non-whitelisted are blocked
- [ ] Arguments are validated
- [ ] No shell injection possible

#### Resources
- [shlex module](https://docs.python.org/3/library/shlex.html)
- Search: "shell injection attack"
- Search: "why shell=True is dangerous"

#### Milestone
Your agent can run safe shell commands.

---

## Phase 7: Tool Chains

Automate multi-tool workflows.

---

### Step 7.1: Chain Definition Format

#### What
Design a YAML/JSON format for defining tool chains without Python.

#### Why
Chains let users automate workflows. But users shouldn't write Python for security reasons.

#### Do Now
1. Create `src/weave/chains/loader.py`
2. Design a format that expresses:
   - Sequential steps
   - Input/output mapping between steps
   - Conditional branching
   - Parallel execution
3. Create example chain files in `chains/` directory
4. Implement loading and validation

#### Success Criteria
- [ ] Chains can be defined in YAML
- [ ] Invalid chains produce helpful errors
- [ ] At least 2 example chains exist

#### Resources
- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- Look at GitHub Actions YAML for inspiration

#### Milestone
You can define and load chain configurations.

---

### Step 7.2: Chain Executor

#### What
Run chain definitions.

#### Why
A format without execution is just documentation.

#### Do Now
1. Create `src/weave/chains/executor.py`
2. Implement:
   - Linear execution (step after step)
   - Data passing between steps
   - Conditional branching
   - Parallel execution (asyncio.gather)
   - Error handling

#### Success Criteria
- [ ] Linear chains work
- [ ] Output from step N is input to step N+1
- [ ] Conditionals branch correctly
- [ ] Parallel steps run concurrently

#### Resources
- [asyncio.gather()](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
- Search: "workflow executor pattern"

#### Milestone
Chains execute end-to-end.

---

### Step 7.3: Built-in Chains

#### What
Create useful pre-built chains.

#### Why
Examples show what's possible and provide immediate value.

#### Do Now
1. Create chain files in `chains/`:
   - `research.yaml`: search → scrape → summarize
   - `test_and_fix.yaml`: run tests → analyze → fix → verify
   - `explain_codebase.yaml`: list files → find entry points → summarize
2. Create `src/weave/chains/builtins.py` to register them
3. Make chains invokable by name in the UI

#### Success Criteria
- [ ] At least 3 built-in chains exist
- [ ] Users can invoke chains by name
- [ ] Chains complete successfully

#### Milestone
Your agent has powerful automation capabilities.

---

## Phase 8: Terminal User Interface

Build the full TUI.

---

### Step 8.1: Layout System

#### What
Create a multi-pane UI: input, conversation, status, sidebar.

#### Why
A single text area isn't usable. Users need clear regions.

#### Do Now
1. Create `src/weave/tui/layout.py`
2. Implement:
   - Screen divided into logical regions
   - Each region independently updatable
   - Resize handling
   - Minimum size enforcement

#### Success Criteria
- [ ] Screen has multiple panes
- [ ] Each pane updates independently
- [ ] Resize works
- [ ] Minimum size is handled

#### Resources
- [curses documentation](https://docs.python.org/3/library/curses.html)
- Search: "curses panel library"

#### Milestone
You have a multi-pane layout.

---

### Step 8.2: Input Handling

#### What
A proper input system with line editing and history.

#### Why
Default curses input is primitive. Good input makes the tool usable.

#### Do Now
1. Create `src/weave/tui/input.py`
2. Implement:
   - Typing, backspace, cursor movement
   - Command history (up/down arrows)
   - Multi-line input
   - Cancel with Escape

#### Success Criteria
- [ ] Arrow keys move cursor
- [ ] Up/down cycles history
- [ ] Long input wraps
- [ ] Escape cancels

#### Resources
- [curses key constants](https://docs.python.org/3/library/curses.html#constants)
- Search: "line editing implementation"

#### Milestone
Input feels like a proper text editor.

---

### Step 8.3: Streaming Output

#### What
Display LLM output as it streams with scrolling and formatting.

#### Why
Streaming is core UX. But you need auto-scroll AND manual scroll-back.

#### Do Now
1. Create `src/weave/tui/output.py`
2. Implement:
   - Token-by-token display
   - Auto-scroll to newest
   - Manual scroll during generation
   - Code block highlighting

#### Success Criteria
- [ ] Tokens stream in
- [ ] Auto-scroll works
- [ ] User can scroll back
- [ ] Code blocks are highlighted

#### Resources
- Search: "curses flicker-free update"
- Search: "terminal markdown rendering"

#### Milestone
Output display is smooth and readable.

---

### Step 8.4: Status & Feedback

#### What
Visual indicators for agent state.

#### Why
Long operations without feedback feel broken.

#### Do Now
1. Create `src/weave/tui/status.py`
2. Implement:
   - State indicator (idle, thinking, executing)
   - Tool execution logging
   - Error highlighting
   - Spinner for long operations

#### Success Criteria
- [ ] State is always visible
- [ ] Tool calls are logged
- [ ] Errors are highlighted
- [ ] Spinner animates

#### Resources
- [curses colors](https://docs.python.org/3/library/curses.html#curses.start_color)
- Search: "terminal spinner Python"

#### Milestone
Users always know what the agent is doing.

---

## Phase 9: Polish

Make it production-ready.

---

### Step 9.1: Configuration

#### What
Allow user configuration of model paths, UI settings, etc.

#### Why
Hardcoded values are hostile to users with different setups.

#### Do Now
1. Create `src/weave/core/config.py`
2. Create `config/default.toml` with all options
3. Implement loading from:
   - Default config
   - User config (`~/.config/weave/config.toml`)
   - Command-line overrides

#### Success Criteria
- [ ] Config file is loaded
- [ ] Missing values use defaults
- [ ] Invalid config shows helpful errors

#### Resources
- [tomllib](https://docs.python.org/3/library/tomllib.html)
- Search: "XDG base directory"

#### Milestone
Your app is configurable.

---

### Step 9.2: Logging

#### What
Comprehensive logging for debugging.

#### Why
When things break, you need to know what happened.

#### Do Now
1. Create `src/weave/core/logging.py`
2. Implement:
   - File-based logging (not stdout)
   - Configurable levels
   - Log all tool calls and LLM interactions

#### Success Criteria
- [ ] Everything is logged
- [ ] Logs don't clutter UI
- [ ] Log level is configurable

#### Resources
- [logging module](https://docs.python.org/3/library/logging.html)
- [logging.handlers](https://docs.python.org/3/library/logging.handlers.html)

#### Milestone
You can debug problems using logs.

---

### Step 9.3: Error Recovery

#### What
Never crash in a way that breaks the terminal or loses data.

#### Why
Curses can leave terminals broken. Crashes can lose hours of work.

#### Do Now
1. Implement cleanup handlers
2. Save conversation on crash
3. Wrap everything in proper exception handling
4. Test by killing the process in various states

#### Success Criteria
- [ ] Any exception restores terminal
- [ ] Conversation is saved even on crash
- [ ] Errors show helpful messages
- [ ] Agent recovers from LLM failures

#### Resources
- [atexit module](https://docs.python.org/3/library/atexit.html)
- [signal module](https://docs.python.org/3/library/signal.html)
- Review `curses.wrapper()`

#### Milestone
Your app is bulletproof.

---

## Final Checklist

Before calling it done:

- [ ] Agent completes multi-step coding tasks
- [ ] Memory persists across restarts
- [ ] All tools are sandboxed
- [ ] Tool chains execute reliably
- [ ] TUI is responsive during inference
- [ ] Resize doesn't crash
- [ ] Ctrl+C exits cleanly
- [ ] Errors show helpful messages
- [ ] You can explain every line you wrote

---

## The Philosophy

This guide withholds code because:

1. **Struggle produces understanding.** Fighting with documentation creates deep knowledge. Copy-pasting creates working code with no understanding.

2. **Documentation is the skill.** Professional developers read docs more than they write code. This is practice.

3. **The code is easy.** Once you understand what and why, implementation is straightforward. The hard part is understanding.

Go build something.
