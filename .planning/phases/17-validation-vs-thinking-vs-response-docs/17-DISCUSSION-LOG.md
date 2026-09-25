# Phase 17: Validation vs thinking vs response docs - Discussion Log

**Date:** 2026-09-25
**Areas discussed:** Onde mora a tríade; Profundidade do texto; Público-alvo; Nunca faça agora

## Area: Onde mora a tríade

| Q | Options | Selected |
|---|---------|----------|
| Where does triad live? | 1 Só rules.py / 2 rules.py+TRIAD.md / 3 só md / 4 you decide | **2** |
| Authoritative source? | 1 TRIAD.md / 2 rules.py / 3 must match / 4 you decide | **1** |
| How rules.py points? | 1 Path+docstring / 2 get_triad_doc_path / 3 docstring only / 4 you decide | **1** |
| Filename? | 1 TRIAD.md / 2 TRIAD.md+PT body / 3 TRIADE.md / 4 you decide | **1** |

## Area: Profundidade do texto

| Q | Options | Selected |
|---|---------|----------|
| Depth? | 1 3 short secs / 2 secs+code pointers / 3 long guide / 4 you decide | **2** (+ future rules files noted; deferred) |
| Future rule files (.md/.yaml/.json)? | 1 hook only / 2 stub folder / 3 defer 100% / 4 you decide | **3** |
| Body language? | 1 PT-BR / 2 EN / 3 mixed / 4 you decide | **1** |
| thinking≠pedagogy? | 1 explicit callout / 2 short phrase / 3 omit / 4 you decide | **1** |
| Pipeline line? | 1 one-liner→AGENTS / 2 none / 3 mermaid / 4 you decide | **1** |

## Area: Público-alvo

| Q | Options | Selected |
|---|---------|----------|
| Audience? | 1 runtime/API / 2 runtime+GSD agents / 3 humans only / 4 you decide | **1** |
| Re-export TRIAD_DOC? | 1 no / 2 yes / 3 you decide | **1** |
| Mention in persona.py? | 1 no / 2 docstring line / 3 you decide | **1** |
| Offline pytest? | 1 yes / 2 no / 3 you decide | **2** |

## Area: Nunca faça agora

| Q | Options | Selected |
|---|---------|----------|
| Never-do this phase? | 1 triad only / 2 triad+never-do in TRIAD / 3 never-do in rules only / 4 you decide | **1** |
| Existing TODO in rules.py? | 1 keep+retarget / 2 remove bullets / 3 you decide | **1** |
| Out-of-scope note in TRIAD? | 1 yes 2–3 lines → P18 / 2 no / 3 you decide | **1** |

## Deferred

- DEF-01: Future loaders for `.md`/`.yaml`/`.json` rule packs
- Detailed never-do + authority map → Phase 18

## Discretion left to implementer

- Exact PT-BR prose; exact code-path list; TODO comment wording
