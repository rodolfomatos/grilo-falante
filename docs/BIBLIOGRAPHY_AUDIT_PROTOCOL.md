# Bibliography Audit Protocol — Implementação Completa

## Resumo (Feynman)

O Bibliography Audit Protocol é como um bibliotecário muito rigoroso:

1. **Pergunta**: "Preciso de referências sobre X?"
2. **Propor**: LLM sugere candidatos
3. **Verificar**: Humano busca as fontes reais
4. **Resumir**: Criar shadow document
5. **Explicar**: Feynman Lite (criança) + Strict (especialista)
6. **Comparar**: O que esperávamos vs o que o artigo diz
7. **Classificar**: FULL/PARTIAL/CONTEXTUAL/MISALIGNED
8. **Decidir**: ACCEPT / REJECT
9. **Guardar**: .bib + maps

---

## 8 Steps

### Step 1: Reference Candidate Proposal
- LLM propõe referências candidatas
- Output: `CandidateReference` (title, authors, year, relevance, domain)

### Step 2: Human Retrieval
- **PDF Upload** (preferido)
- **Excerpt** (fallback)
- Input: citation + abstract + passages

### Step 3: Shadow Document Creation
- Metadata: title, authors, year, venue, DOI
- Claims extraídas
- Evidence

### Step 4: Double Feynman Analysis
- **Lite**: Resumo simples (criança)
- **Strict**: Interpretação precisa (especialista)
- **Not Claim**: O que NÃO klaim

### Step 5: Expectation vs Reality
- Expected: O que pensávamos que apoiava
- Reality: O que realmente diz
- Gap: MINIMAL / MODERATE / SIGNIFICANT

### Step 6: Claim Coverage
| Classification | Significado |
|---------------|------------|
| FULL_SUPPORT | Fonte apoia diretamente |
| PARTIAL_SUPPORT | Fonte apoia parcialmente |
| CONTEXTUAL_SUPPORT | Fonte dá contexto |
| MISALIGNED | Fonte não apoia |

### Step 7: Human Decision
| Decision | Significado |
|----------|------------|
| ACCEPT | fully suitable |
| ACCEPT_WITH_LIMITATION | narrower wording |
| REJECT | não usar |

### Step 8: Integration
- `.bib` file (BibTeX)
- Validation Log (JSON)
- Claim-Citation Map (JSON)

---

## Uso

```python
from app.services.bibliography_auditor import BibliographyAuditor

auditor = BibliographyAuditor()

result = auditor.audit(
    topic="neural networks consciousness",
    target_claim="consciousness emerges from neural complexity",
    human_decision="ACCEPT"
)
```

---

## Outputs

```
graphify-out/
├── references.bib              # @article{smith2023,...
├── reference_validation_log.json
└── claim_citation_map.json
```

---

## Integração

| Sistema | Conexão |
|---------|--------|
| Ir à Escola | Pode propor refs candidatas |
| Scientific Compiler | Pode validar artigos |
| MemPalace | Guarda shadow docs |

---

*Data: 2026-04-13*
*Protocol: gf_bibliography_audit_prompt.md*