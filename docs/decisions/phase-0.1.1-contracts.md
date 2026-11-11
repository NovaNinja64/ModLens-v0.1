# Phase 0.1.1 — Shared contracts and exception foundation

**Status:** Implementation prepared on `foundation/0.1.1-contracts`  
**Scope:** Shared data contracts and the core exception hierarchy only.

## Architecture decisions

- Shared contracts live in `src/modlens/models/`. This is a deliberate, documented deviation from the original architecture layout that placed shared contracts directly under `core/`. The models package is independent of other internal ModLens packages.
- Contracts use Pydantic 2, immutable/frozen models, strict extra-field rejection, UUID identity, and `pathlib.Path` for filesystem locations.
- No model performs filesystem probing or imports PySide6.
- Path serialization uses Pydantic's native JSON-mode serialization and validation.
- Steam game installations must carry a storefront library ID. Other storefronts and manually selected installations may omit it.
- Storefront installation, storefront library, and game installation are distinct entities. A library's availability is a discovery snapshot, not a permanent property.
- Manager application, configured manager instance, and named profile are separate entities.
- Discovery results are typed aggregates; progress events are immutable and framework-neutral.
- Discovery provenance is represented in memory by `DiscoveryMetadata`. Persistence should flatten its fields into ordinary database columns; database mapping is deferred to the storage milestone.
- UUIDs are intended to be stored in SQLite as canonical hyphenated TEXT values.
- Cancellation is session-level: valid partial results may be retained, but unfinished entities are not fabricated. Session status is `CANCELLED`.
- The exception hierarchy does not shadow Pydantic's `ValidationError`.

## Files introduced

- `src/modlens/models/base.py`
- `src/modlens/models/enums.py`
- `src/modlens/models/installations.py`
- `src/modlens/models/managers.py`
- `src/modlens/models/discovery.py`
- `src/modlens/models/__init__.py`
- `src/modlens/core/exceptions.py`
- `tests/test_models.py`

## Acceptance boundary

This milestone establishes contracts and their unit tests. It does not implement discovery logic, persistence mappings, service registration, database migrations, application lifecycle, or cancellation orchestration. Those remain in their assigned later milestones.
