# ModLens Project Handoff

## Current milestone
Phase 0 — foundation scaffold.

## Decisions
- Windows 10 and Windows 11 initially.
- Skyrim Special Edition / Anniversary Edition is the first game target.
- Initial manager integrations: Vortex and Mod Organizer 2.
- Manual and mixed installations are first-class supported setups.
- Local-first data storage with optional future cloud sync.
- Python + PySide6 desktop UI; SQLite local database.
- Portable and installer distributions are both planned.
- Read-only behavior is the default; no automatic game/mod changes.
- Never hardcode a drive letter or assume a standard installation path.

## Prototype audit status
The previous prototype received a static source audit, not runtime validation.
The scanner requires replacement; startup, documentation, and launcher need
improvement. The next major feature milestone is universal discovery.

## Next milestones
1. Validate this foundation on the user's Windows machine.
2. Add automated tests and improve migration handling.
3. Implement Steam library discovery and game installation detection.
4. Add Vortex and MO2 detection as independent adapters.
5. Add manual path selection and persist verified locations.

## Continuity rule
Update this file at meaningful milestones. Do not wait until the end of a chat.
