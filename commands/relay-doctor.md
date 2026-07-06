---
description: Run a Relay preflight self-check on this machine - reports which capabilities (core triggers, git Repository State, Ollama local mode) are available.
allowed-tools: [Bash, PowerShell, Glob]
---

# /relay-doctor Command

Run Relay's self-check and show the user which capabilities work on their device.

## Instructions

1. **Locate the doctor script** in this plugin's `scripts/` directory. Prefer `${CLAUDE_PLUGIN_ROOT}/scripts/`. If unavailable, glob: `~/.claude/plugins/cache/grove-plugins/relay/*/scripts/doctor.*`

2. **Run the OS-appropriate one:**
   - Windows: `powershell -NoProfile -File "<path>\doctor.ps1"`
   - macOS/Linux: `python3 "<path>/doctor.py"`

3. **Show the output verbatim** to the user, then give a one-line summary of what works and what (optionally) they could add (git for Repository State, Ollama for local mode / auto-recovery).

Core handoff triggers work everywhere with no extra dependencies; git and Ollama only unlock optional capabilities.
