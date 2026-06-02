# Historical Files Register

This file is a register, not an action plan.

Agents should record suspected historical files here before changing them. Any cleanup should be handled as a separate explicit task.

## Known historical or lower-priority areas

| Path | Status | Notes |
|---|---|---|
| `combined/index.html` outputs | Historical / debug only | Existing docs describe this as an early experimental output. It must not become the production mainline. |
| `tests/manual_archive/` | Archive | Useful for history, but not an active entrypoint. |
| `outputs/` | Generated output | Useful for local review artifacts, not source entrypoints. |
| `test_outputs/` | Generated test output | Useful for local testing only. |

## Cleanup review rule

Before changing any historical file, an agent must report:

1. Exact path
2. Why it is considered historical
3. Whether it is referenced by active code, tests, docs, or commands
4. Proposed action
5. Verification command after the change

## Current status

No cleanup action is performed by this repository-index task.
