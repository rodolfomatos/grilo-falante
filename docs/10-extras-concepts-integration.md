# 10-extras-concepts-integration.md

This document summarizes the most valuable concepts from the extras directory (/home/rodolfo/Desktop/Grilo_Falante/extras/) that should be integrated into the project.

---

## 1. Five Core Mechanisms (from documento_fundador)

| Mechanism | Function | Integration |
|-----------|----------|-------------|
| **Índices** | Map what was discussed; reduce implicit memory dependency | Add to loader_kernel as tracking index |
| **Backlog governado** | Single source of truth; separates proposal from promotion | Extend INA (Índice Normativo de Artefactos) |
| **Origem explícita** | Every decision/patch must indicate source chat | Add `origin_chat_id` field to GMIF nodes |
| **Promoção humana explícita** | Nothing canonical by inference; all promotion declared | F7 already implements this |
| **Documentos sombra** | Preserve decisions/ideas without reinterpretation | Add new artefact type |

---

## 2. Key Principles

### From capsula_conceptual_o_caso_do_relogio.md

1. **Verification is delegable; validation is not** — Verification can be automated; validation requires human judgment
2. **Volatile facts demand local + immediate validation** — Temporal claims need real-time check
3. **Authority depends on procedure, not fluency** — Method over style

### From ARTIGO_A_FECHO_DO_LOOP_EPISTEMICO

- **Norma não substitui método** — Norms alone don't provide inference
- Gap between acceptance and inference needs instrumentation

---

## 3. Phase Model (from grilo_falante_uni_v1.6.4)

| Phase | Description | Current State Machine |
|-------|-------------|----------------------|
| F0 — Exploração | Non-productive exploration | Not yet implemented |
| F1 — Ancoragem e Validação | Anchoring + validation | Partially in F1 |
| F2 — Construção Controlada | Controlled building | F2, F3, F4 |
| F3 — Consolidação e Revisão | Consolidation + review | F6, F7, F8 |

---

## 4. Mapping to Existing Components

### State Machine (state_machine.py)
- **F0 (Exploration)**: Add new state for non-productive exploration
- Preserve current F1-F8 progression
- Current handler returns: `{"phase": str, "status": "continue"|"terminal", "output": {...}}`

### LOADER/KERNEL (loader_kernel.py)
- **Current**: SystemUseRecord tracks source, context, effect (lines 26-32)
- **Add**: origin tracking for loaded content via `origin_chat` field
- **Add**: verification_level distinction (SystemUseRecord already has `artefact_type`)
- **Current artefact types**: "Objeto Digital" (line 27)

### GMIF Nodes
- **Current**: `gf_id`, `gmif_type`, `legitimacy` fields
- **Add**: `origin_chat` field (from documento_fundador)
- **Add**: `verification_level` field (VERIFIED / VALIDATED / SUSPENDED)

### INA (Índice Normativo de Artefactos)
- Current: tracked via Ledger in grilo_falante_uni_v1.6.4
- **Expand**: Add artefact type tracking for Documento Sombra, Cápsula Conceptual, Objeto Digital

---

## 5. New Artefact Types

### Documento Sombra
- Preserves decisions/ideas without reinterpretation
- Assumes explicit technical limits

### Cápsula Conceptual
- Extracted and promoted concept
- Pedagogical + methodological function

### Objeto Digital
- Digital artifact with provenance tracking

---

## 6. Next Steps

1. Update state_machine.py with F0 phase
2. Extend GMIF schema with new fields
3. Implement verification/validation distinction in loader_kernel.py
4. Add artefact type tracking to INA

---

## Files Analyzed

- /home/rodolfo/Desktop/Grilo_Falante/extras/documento_fundador_governacao_cognitiva_assistida.md
- /home/rodolfo/Desktop/Grilo_Falante/extras/capsula_conceptual_o_caso_do_relogio.md
- /home/rodolfo/Desktop/Grilo_Falante/extras/ARTIGO_A_FECHO_DO_LOOP_EPISTEMICO_ESQUELETO.md
- /home/rodolfo/Desktop/Grilo_Falante/extras/grilo_falante_uni_v1.6.4.md