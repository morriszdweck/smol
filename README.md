# Smol

A tiny coding agent that connects an OpenAI-compatible chat model to your shell.

Smol- stays in one Python file and uses only the standard library. Give it a task, let the model propose a command, see that command in the terminal, and feed the output back into the conversation. It repeats this loop until the task is finished.

## Why use Smol

Use Smol- when you want an agent loop without a framework around it:

- **Minimal and cheap** Because of the lack of excessive and unnecessary tools, it costs significantly cheaper compared to other coding agents.
- **Small enough to inspect.** The whole agent is a single script you can read, copy, or modify.
- **No dependency setup.** There is no virtual environment, package install, or SDK to maintain.
- **Provider-independent.** Point it at any compatible `/v1` endpoint and choose the model ID that endpoint exposes.
- **Visible execution.** Each shell command is printed before it runs, and its output becomes the next part of the conversation.
- **Useful in a plain terminal.** It supports one-shot tasks, an interactive session, and fresh conversations without a dashboard.

It is a good fit for quick coding tasks, personal or self-hosted endpoints, and experimenting with different models while keeping the control loop easy to understand.

## How it works

1. Smol- sends the task and conversation history to your selected chat model.
2. The model can return a command in a `<cmd>...</cmd>` block.
3. Smol- runs that command in the current working directory and captures its output.
4. The output is sent back to the model, which can continue or answer in plain text.

Each command runs in a fresh shell. Use `&&` or absolute paths when a task needs to carry state between commands.

## Install

The installer checks for `python3` first. If it is missing, it uses Homebrew on macOS or `apt-get`, `dnf`, or `pacman` on Linux, then downloads the executable to `~/.local/bin`:

```sh
command -v python3 >/dev/null 2>&1 || { if command -v brew >/dev/null 2>&1; then brew install python; elif command -v apt-get >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y python3; elif command -v dnf >/dev/null 2>&1; then sudo dnf install -y python3; elif command -v pacman >/dev/null 2>&1; then sudo pacman -Sy --noconfirm python; else echo 'python3 is required; install it and rerun this command.' >&2; exit 1; fi; } && mkdir -p ~/.local/bin && curl -fsSL https://raw.githubusercontent.com/morriszdweck/smol/main/smol.py -o ~/.local/bin/smol && chmod +x ~/.local/bin/smol
```

If `~/.local/bin` is not on your `PATH`, add this line to `~/.bashrc` or `~/.zshrc`, then open a new shell:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

The installer needs `curl` and a POSIX shell. If no supported package manager is available, install Python 3 manually and rerun the command.

## Quick start

Configure the endpoint and model:

```sh
smol login
```

Smol- asks for a base URL, fetches the available models, and prints their full IDs. Enter the model ID itself, such as `qwen-z/qwen3.8-flash`; do not enter a menu number or `#2`.

Then run a task:

```sh
smol "find the failing test and explain the likely cause"
```

Or start an interactive session:

```sh
smol
```

## Commands

| Command | What it does |
| --- | --- |
| `smol login` | Configure or switch the endpoint and model. |
| `smol "task"` | Run one task and exit after the agent responds. |
| `smol` | Start an interactive session. |
| `/new` | Clear the current conversation and start fresh. |
| `/login` | Reconfigure the provider from inside a session. |
| `/exit`, `/quit`, `/q`, or `Ctrl-D` | Leave the session. |

From a source checkout, the equivalent commands are `python3 smol.py login`, `python3 smol.py "task"`, and `python3 smol.py`.

## Configuration

`smol login` saves the configuration in `~/.smol.json` with restricted `0600` permissions. These environment variables override the saved values:

| Variable | Meaning |
| --- | --- |
| `SMOL_BASE` | OpenAI-compatible base URL, including `/v1` when required. |
| `SMOL_KEY` | API key. |
| `SMOL_MODEL` | Model ID. |

The endpoint should provide the usual `/models` and `/chat/completions` routes.

## Safety and limits

Smol- executes arbitrary shell commands in the current working directory. It does not provide a sandbox or an approval prompt. Review the command shown in the terminal, and use a scratch directory or container for untrusted tasks. Keep API keys out of prompts and do not commit `~/.smol.json`.

## License

MIT. See [LICENSE](LICENSE).
