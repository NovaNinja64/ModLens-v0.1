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

ModLens requires Python 3.11 or newer.

Check your installed Python version:

```powershell
py --version
```

Create a virtual environment from the repository folder:

```powershell
py -m venv .venv
```

Install the pinned development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
```

Install ModLens from the local repository:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

Launch ModLens:

```powershell
.\.venv\Scripts\python.exe -m modlens
```

Using the virtual environment's Python executable directly avoids requiring PowerShell script activation permissions.


## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```


## Run code quality checks

```powershell
.\.venv\Scripts\python.exe -m ruff check src/modlens tests
```


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
