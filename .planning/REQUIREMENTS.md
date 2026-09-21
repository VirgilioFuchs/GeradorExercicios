# Requirements: Gerador de Exercícios com IA

**Defined:** 2026-09-21  
**Milestone:** v2.1 Lotes dinâmicos  
**Core Value:** Gerar exercícios de matemática confiáveis e estruturados com validação de formato — agora também via `service.generate_batch` para um host embutir o gerador.

## v2.1 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### BATCH — Contrato do lote

- [ ] **BATCH-01**: Request aceita plano/spec por item (`itens` ou equivalente) além do modo uniforme
- [ ] **BATCH-02**: Invariante `quantidade` ↔ tamanho do plano/specs (falha cedo se divergir)
- [ ] **BATCH-03**: Cada `Exercise` no JSON ecoa `dificuldade` (e campos de tipo se existirem depois)
- [ ] **BATCH-04**: Request uniforme (`dificuldade` + `quantidade`) continua válido (compat)

### PROMPT — Prompt misto

- [ ] **PROMPT-01**: Prompt enumera slot → dificuldade (item-a-item) quando o plano misto está presente

### VAL — Validação (sem overhaul de math)

- [ ] **VAL-01**: Validator checa count + adesão por slot ao plano
- [ ] **VAL-02**: RELY + math_check atuais permanecem (sem redesign)

### UX — CLI / wizard

- [ ] **UX-01**: Wizard com plano compacto (contagens por banda de dificuldade)
- [ ] **UX-02**: Argparse com plano compacto (ex. `--plano`)

### CAP — Quantidade

- [ ] **CAP-01**: Manter cap de quantidade **40** neste milestone

## Future Requirements

Deferred; tracked but not in current roadmap.

### CAP

- **CAP-02**: Subir cap finito (número a decidir na discuss; já no radar)

### TIPO — Tipo de raciocínio (aberto)

- **TIPO-OPEN**: Pesquisa/discuss sobre “tipo de raciocínio” (pedagógico vs API `reasoning_effort` vs taxonomia) — **não** fechado neste milestone; opções além do binário enum-agora / só-dificuldade

### Packaging / ops (parked)

- **PKG-01**: Packaging `pyproject.toml` + rename `exercise_ai/`
- **OBS-01**: Usage/cost/`run_id`/provider efetivo junto com o lote
- **LOG-01**: print → logging

## Out of Scope

| Feature | Reason |
|---------|--------|
| Chunking multi-call para lotes grandes | Adiar até CAP-02 / necessidade real |
| Overhaul math_check / validação semântica | Fora do foco de lotes mistos |
| BNCC (SEED-001) | Dormant |
| Imagens / storytelling (SEED-003 B/C) | Dormant |
| Demo UX nova para lotes | Host/demo usam `GenerationRequest` enriquecido; UX de plano é CLI/wizard |
| Per-item API `reasoning_effort` | Anti-feature; effort permanece run-level |

## Traceability

Filled during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BATCH-01 | — | Pending |
| BATCH-02 | — | Pending |
| BATCH-03 | — | Pending |
| BATCH-04 | — | Pending |
| PROMPT-01 | — | Pending |
| VAL-01 | — | Pending |
| VAL-02 | — | Pending |
| UX-01 | — | Pending |
| UX-02 | — | Pending |
| CAP-01 | — | Pending |

**Coverage:**
- v2.1 requirements: 10 total
- Mapped to phases: 0
- Unmapped: 10 (roadmap next)

---
*Requirements defined: 2026-09-21*  
*Last updated: 2026-09-21 after milestone v2.1 scoping*
