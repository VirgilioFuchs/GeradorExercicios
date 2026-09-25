---
schema_version: 1
open_count: 2
waived_count: 0
fixed_count: 0
total_count: 2
last_updated: 2026-09-25T13:04:14.515Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 16 | stub | exercise-ai/skills/generation/persona.py |  | PT-BR PLACEHOLDER persona string (D-05 intentional) | open |  | 2026-09-25T13:04:13.416Z |  |
| 2 | 16 | stub | exercise-ai/skills/generation/rules.py |  | pass + TODO never-do only (D-06/D-09; real rules 17-18) | open |  | 2026-09-25T13:04:14.515Z |  |

````json
[
  {
    "id": 1,
    "kind": "stub",
    "phase": "16",
    "file": "exercise-ai/skills/generation/persona.py",
    "line": null,
    "description": "PT-BR PLACEHOLDER persona string (D-05 intentional)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-25T13:04:13.416Z",
    "resolved_at": null
  },
  {
    "id": 2,
    "kind": "stub",
    "phase": "16",
    "file": "exercise-ai/skills/generation/rules.py",
    "line": null,
    "description": "pass + TODO never-do only (D-06/D-09; real rules 17-18)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-25T13:04:14.515Z",
    "resolved_at": null
  }
]
````
