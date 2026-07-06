#!/usr/bin/env python3
"""doctor.py - Relay preflight self-check (macOS/Linux).
Reports which Relay capabilities are available on THIS machine."""
import os
import platform
import shutil
import subprocess
import sys
import urllib.request

print("=== Relay doctor ===")
print("OS      : {} {}".format(platform.system(), platform.release()))
print("Python  : {}".format(sys.version.split()[0]))
print()

# Core handoff triggers - if this runs, Python 3 is available.
print("[ OK ] Core handoff triggers (auto handoff at token budget, /handoff)")

# git -> Repository State depth
if shutil.which("git"):
    try:
        ver = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        ver = "git"
    print("[ OK ] git found ({})  ->  handoffs include Repository State".format(ver))
else:
    print("[ -- ] git not found              ->  handoffs omit the Repository State section")

# Ollama -> local mode + auto-recovery
url = os.environ.get("RELAY_OLLAMA_URL", "http://localhost:11434").rstrip("/")
try:
    import json
    with urllib.request.urlopen(url + "/api/tags", timeout=4) as r:
        tags = json.loads(r.read())
    models = ", ".join(m.get("name", "") for m in (tags.get("models") or [])) or "(none pulled - run: ollama pull gemma4)"
    print("[ OK ] Ollama reachable at {}".format(url))
    print("        models: {}".format(models))
    print("        ->  /handoff-local, relay-recover, and 429 auto-recovery enabled")
except Exception:
    print("[ -- ] Ollama not reachable at {}".format(url))
    print("        ->  local mode + auto-recovery disabled (install: https://ollama.com)")

print()
print("Core triggers work with zero of the optional pieces above; git and Ollama only add capabilities.")
