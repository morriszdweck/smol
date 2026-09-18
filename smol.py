#!/usr/bin/env python3
# Smol- — a smol, zero-dependency coding agent for any OpenAI-compatible endpoint
# setup:    python3 smol.py login      (saves provider to ~/.smol.json)
# one-shot: python3 smol.py "task"
# repl:     python3 smol.py            (or paste this whole file into python3)
# overrides: SMOL_BASE / SMOL_KEY / SMOL_MODEL env vars beat the saved config
import sys, os, json, subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from getpass import getpass

CFG = os.path.expanduser("~/.smol.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
SYS = """You are Smol-, a smol coding agent working in the current directory.
To act, reply with exactly one command block:
<cmd>shell command here</cmd>
Text outside the block is shown to the user first. The command's
output is returned as your next message. Each command runs in a
fresh shell in the cwd, so chain with && or use absolute paths.
Iterate until the task is done, then reply with plain text only."""

def conf():
    c = {}
    try:
        c = json.load(open(CFG))
    except Exception:
        pass
    c["base"] = os.environ.get("SMOL_BASE", c.get("base", "")).rstrip("/")
    c["key"] = os.environ.get("SMOL_KEY", c.get("key", "none"))
    c["model"] = os.environ.get("SMOL_MODEL", c.get("model", ""))
    return c

def api(c, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(c["base"] + path, data=data, headers={"Content-Type": "application/json", "Authorization": "Bearer " + c["key"], "User-Agent": UA, "Accept": "application/json"})
    try:
        return json.loads(urlopen(req, timeout=300).read())
    except HTTPError as e:
        raise SystemExit("http %s: %s" % (e.code, e.read().decode(errors="replace")[:300]))
    except Exception as e:
        raise SystemExit("api unreachable: %s" % e)

def models(c):
    return [m["id"] for m in api(c, "/models")["data"]]

def login():
    old = conf()
    base = (input("base url incl /v1 [%s]: " % old.get("base", "")) or old.get("base", "")).strip().rstrip("/")
    key = getpass("api key (blank = none): ").strip() or "none"
    if not base:
        print("Smol- needs a base url")
        return
    c = {"base": base, "key": key}
    try:
        ms = models(c)
    except SystemExit:
        ms = []
    if ms:
        print("models:")
        for i, m in enumerate(ms):
            print("  %2d) %s" % (i + 1, m))
        pick = input("pick a model # or type an id: ").strip()
        if pick.isdigit() and 0 < int(pick) <= len(ms):
            c["model"] = ms[int(pick) - 1]
        elif pick:
            c["model"] = pick
    if not c.get("model"):
        c["model"] = input("model id: ").strip()
    fd = os.open(CFG, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(c, f)
    print("saved to %s — Smol- is ready (model: %s)" % (CFG, c["model"]))

def run(cmd):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
        return (p.stdout + p.stderr)[:8000] or "(no output)"
    except Exception as e:
        return "error: " + str(e)

def chat(c, msgs):
    r = api(c, "/chat/completions", {"model": c["model"], "messages": msgs, "temperature": 0, "max_tokens": 4096})
    return r["choices"][0]["message"]["content"] or ""

def agent(c, msgs, task):
    msgs = msgs + [{"role": "user", "content": task}]
    for _ in range(40):
        out = chat(c, msgs)
        msgs.append({"role": "assistant", "content": out})
        if "<cmd>" not in out:
            print(out)
            return msgs
        head, cmd = out.split("<cmd>", 1)
        cmd = cmd.split("</cmd>", 1)[0].strip()
        if head.strip():
            print(head.strip())
        print("\033[36m$ %s\033[0m" % cmd)
        res = run(cmd)
        print(res)
        msgs.append({"role": "user", "content": "<output>\n%s\n</output>" % res})
    print("(hit 40-step cap)")
    return msgs

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        login()
        return
    c = conf()
    if not c["base"] or not c["model"]:
        print("Smol- isn't configured. run: python3 smol.py login")
        return
    print("Smol-  %s  @  %s" % (c["model"], c["base"]))
    msgs = [{"role": "system", "content": SYS}]
    if len(sys.argv) > 1:
        agent(c, msgs, " ".join(sys.argv[1:]))
        return
    print("type a task. /new = fresh chat, /login = switch provider, /exit or ctrl-d = quit")
    while True:
        try:
            task = input("\ntask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if task in ("/exit", "/quit", "/q"):
            return
        if task == "/new":
            msgs = [{"role": "system", "content": SYS}]
            print("(new chat)")
        elif task == "/login":
            login()
            c = conf()
            if c["base"] and c["model"]:
                print("Smol-  %s  @  %s" % (c["model"], c["base"]))
        elif task:
            try:
                msgs = agent(c, msgs, task)
            except KeyboardInterrupt:
                print("\n(interrupted)")

if __name__ == "__main__":
    main()
