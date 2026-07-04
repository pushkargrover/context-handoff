---
description: Generate a session handoff using your LOCAL Ollama model (zero Anthropic tokens). Great before you hit a limit, or to test local recovery. Requires Ollama installed.
argument-hint: [session-index]
allowed-tools: [Bash, PowerShell, Glob]
---

# /handoff-local Command

Generate a handoff for the current session using a **local** model via Ollama, costing **zero Anthropic tokens**. This is the same engine as the standalone `relay-recover` lockout tool.

## Instructions

1. **Locate the recovery script** in this plugin's `scripts/` directory. Prefer `${CLAUDE_PLUGIN_ROOT}/scripts/`. If that variable is unavailable, glob for it:
   `~/.claude/plugins/cache/grove-plugins/relay/*/scripts/relay-recover.*`

2. **Run the OS-appropriate script**, passing `$ARGUMENTS` through (a bare number selects that session; empty = the most recent / current session):
   - Windows: `powershell -NoProfile -File "<path>\relay-recover.ps1" $ARGUMENTS`
   - macOS/Linux: `python3 "<path>/relay-recover.py" $ARGUMENTS`

3. This takes a couple of minutes (the local model is slower than Claude). When it finishes, **report the `Handoff saved to:` path** to the user.

## Notes

- Requires **Ollama** installed and running, with at least one model pulled (e.g. `ollama pull gemma4`). If the script reports it can't reach Ollama, tell the user to install/start it (https://ollama.com).
- Choose the model with the `RELAY_OLLAMA_MODEL` env var, or the script auto-detects the first installed model.
- For recovery **after** a lockout (when Claude can't run this command), the user runs `relay-recover` directly in a terminal instead — see the README.
