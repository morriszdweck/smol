# Smol-

Smol- is a single-file, zero-dependency coding agent for any OpenAI-compatible endpoint; it runs an agentic shell-command loop with conversation memory and works as a script or when pasted directly into the `python3` REPL.

## Install

```sh
mkdir -p ~/.local/bin && curl -fsSL https://raw.githubusercontent.com/morriszdweck/smol/main/smol.py -o ~/.local/bin/smol && chmod +x ~/.local/bin/smol
```

The install requires `python3` and uses only the standard library; nothing needs to be installed with `pip`. If `~/.local/bin` is not on your `PATH`, add `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc` or `~/.zshrc`.

## Usage

If you installed Smol- with the one-liner above, run the installed command:

```sh
smol login
```

If `~/.local/bin` is not on your `PATH`, use `~/.local/bin/smol login` or add the `PATH` export shown above. The `python3 smol.py ...` forms below are for running from a checkout that contains `smol.py`; installing the one-liner does not create `~/smol.py`.

- `smol login` (or `python3 smol.py login` from a checkout) runs interactive provider setup and saves the configuration to `~/.smol.json` with `0600` permissions.
- `smol "task"` (or `python3 smol.py "task"` from a checkout) runs a one-shot task.
- `smol` (or `python3 smol.py` from a checkout) starts an interactive session with `/new`, `/login`, and `/exit` commands.
- Environment overrides: `SMOL_BASE`, `SMOL_KEY`, and `SMOL_MODEL`.

## Security

The agent executes arbitrary shell commands in your current working directory. Review commands before and while they run; use a scratch directory or container if paranoid.
