#!/usr/bin/env python3
"""Unit tests for relay-recover.py parsing logic (no Ollama required).

Covers the bug-prone pure functions: content-block extraction, ANSI/control-char
sanitization, transcript truncation, and session selection. The Ollama HTTP call
itself is verified live (see README), not mocked here.

Run: python tests/test-recover.py    Exit 0 = pass, 1 = fail.
"""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "relay_recover", os.path.join(HERE, "..", "scripts", "relay-recover.py"))
rr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rr)

passed = 0
failed = 0


def check(cond, name):
    global passed, failed
    if cond:
        passed += 1
        print("  PASS  " + name)
    else:
        failed += 1
        print("  FAIL  " + name)


print("relay-recover.py parsing tests")
print("------------------------------")

# text_from_content: plain string
check(rr.text_from_content("hello") == "hello", "plain string content")

# text_from_content: mixed blocks
blocks = [
    {"type": "text", "text": "wrote a file"},
    {"type": "tool_use", "name": "Edit"},
    {"type": "tool_result", "content": "x" * 500},
]
out = rr.text_from_content(blocks)
check("wrote a file" in out, "text block extracted")
check("[used tool: Edit]" in out, "tool_use summarized")
check("[tool result:" in out and out.endswith("...]"), "tool_result truncated to 200 chars")

# sanitization: ANSI escape sequences and control chars stripped
raw = "USER: hi\x1b[?25lthere\x1b[0m\x07\x00 end"
fixture = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
import json as _json
fixture.write(_json.dumps({"type": "user", "message": {"role": "user", "content": raw}}) + "\n")
fixture.write(_json.dumps({"type": "assistant", "message": {"role": "assistant",
              "content": [{"type": "text", "text": "ok done"}]}}) + "\n")
fixture.close()
convo = rr.clean_conversation(fixture.name)
check("\x1b" not in convo, "ESC bytes removed")
check("\x07" not in convo and "\x00" not in convo, "control bytes removed")
check("hithere end" in convo.replace("  ", " "), "visible text preserved after stripping")
check("ASSISTANT: ok done" in convo, "assistant turn included")
os.unlink(fixture.name)

# truncation: long transcript keeps head + tail, stays within budget
long_fixture = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
for i in range(4000):
    long_fixture.write(_json.dumps({"type": "user", "message": {"role": "user",
                       "content": "message number %d here" % i}}) + "\n")
long_fixture.close()
big = rr.clean_conversation(long_fixture.name)
check(len(big) <= rr.MAX_CHARS + 100, "long transcript truncated to budget")
check("message number 0 here" in big, "head (goal) preserved")
check("message number 3999 here" in big, "tail (recent state) preserved")
check("trimmed to fit" in big, "truncation marker present")
os.unlink(long_fixture.name)

# empty / garbage lines tolerated
g = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
g.write("\n")
g.write("not json at all\n")
g.write(_json.dumps({"type": "user", "message": {"role": "user", "content": "real msg"}}) + "\n")
g.close()
check("USER: real msg" in rr.clean_conversation(g.name), "garbage/blank lines skipped")
os.unlink(g.name)

# git_state: non-repo returns empty
import subprocess as _sp
nonrepo = tempfile.mkdtemp()
check(rr.git_state(nonrepo) == "", "git_state returns empty for a non-repo dir")
check(rr.git_state("/does/not/exist") == "", "git_state returns empty for a missing dir")

# git_state: real repo with an uncommitted change captures the facts
def _has_git():
    try:
        _sp.run(["git", "--version"], capture_output=True, timeout=10)
        return True
    except (OSError, _sp.SubprocessError):
        return False

if _has_git():
    repo = tempfile.mkdtemp()
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    _sp.run(["git", "-C", repo, "init", "-q"], capture_output=True, env=env)
    with open(os.path.join(repo, "a.txt"), "w") as f:
        f.write("hello\n")
    _sp.run(["git", "-C", repo, "add", "a.txt"], capture_output=True, env=env)
    _sp.run(["git", "-C", repo, "commit", "-qm", "init"], capture_output=True, env=env)
    with open(os.path.join(repo, "b.txt"), "w") as f:
        f.write("new file\n")          # uncommitted change
    gs = rr.git_state(repo)
    check("## Repository State" in gs, "git_state emits a Repository State section")
    check("b.txt" in gs, "git_state lists the uncommitted file")
    check("Last commit" in gs and "init" in gs, "git_state includes the last commit")
else:
    print("  SKIP  git not available for git_state repo test")

print("------------------------------")
print("%d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
