# ModLens

**See deeper. Find the problem. Fix your game.**

ModLens is a local-first Windows desktop application for inspecting modded game installations and helping diagnose problems. The initial target is Skyrim Special Edition / Anniversary Edition, with support planned for Steam, Vortex, Mod Organizer 2, manual installations, and mixed setups.

## Current status

This repository contains the initial **Phase 0 foundation scaffold**. It establishes the application package, configuration, logging, SQLite initialization, background task abstraction, a basic PySide6 window, and starter tests. It does **not yet perform game or mod discovery**.

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer
- Git (optional, for source control)
- GitHub Desktop (optional, for a graphical Git workflow)

## Set up

From the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m modlens
```

If PowerShell blocks activation, run the application using the virtual environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m modlens
```

## Run tests

```powershell
pytest
```

## Data and safety

- Application data is stored under the current user's local application-data directory.
- The initial foundation does not modify game files, mod files, manager profiles, or load order.
- Discovery and scanning features will be read-only by default.
- Do not place credentials, API keys, personal game logs, or private configuration files in Git.

## Development roadmap

1. Foundation and prototype audit
2. Universal game and manager discovery
3. Unified inventory for manager-managed, manual, and mixed setups
4. Skyrim scanning and deterministic diagnostics
5. Main UI and reporting
6. AI Troubleshooter
7. Profiles, history, and backups
8. Live Assist
9. Module system and additional games
10. Packaging and release
