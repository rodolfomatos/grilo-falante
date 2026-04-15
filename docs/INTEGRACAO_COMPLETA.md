# INTEGRAÇÃO COMPLETA — Scientific Compiler + Ir à Escola

## Resumo (Feynman)

O sistema "Scientific Compiler + Ir à Escola" funciona assim:

1. **Artigo entra** → Scientific Compiler
2. **Claims extraídas** → Verifica no MemPalace (como Ir à Escola)
3. **Gaps encontrados** → Active Search
4. **Síntese gerada** → Explica como Feynman
5. **Grafo construído** → GMIF graph DOT

---

## Ficheiros Criados

| Ficheiro | Função | Linhas |
|----------|-------|--------|
| `gap_detector.py` | Deteta factos desconhecidos | 250 |
| `active_search.py` | Procura em 3 fontes | 180 |
| `feynman_synthesize.py` | Síntese dual | 150 |
| `why_loop.py` | Loop de "porquês?" | 130 |
| `ir_a_escola.py` | Orquestrador | 200 |
| `scientific_compiler.py` | 12 stages | 450 |
| `gf_scientific_compiler_v_2_spec.md` | Spec original | - |
| `IR_A_ESCOLA_CONCEITO.md` | Conceito | - |
| `ANALISE_HOSTIL_IR_A_ESCOLA.md` | Análise | - |
| `ANALISE_HOSTIL_SC_V2.md` | Análise SC | - |

---

## Uso

### Scientific Compiler (artigos científicos)
```bash
python3 -m app.services.scientific_compiler /path/to/article.md
```

### Ir à Escola (qualquer conversa)
```bash
python3 -m app.services.ir_a_escola "Alan Turing nasceu em 1912"
```

### Pipeline Completo
```python
from app.services.scientific_compiler import ScientificCompiler
from app.services.ir_a_escola import IrAEscolaOrchestrator

# 1. Analisa artigo
sc = ScientificCompiler()
result = sc.compile("/path/to/article.md")

# 2. Se há gaps, procura
if result.gaps_detected:
    orchestrator = IrAEscolaOrchestrator()
    escola_result = orchestrator.run(result.original_message)
```

---

## Arquitetura Integrada

```
┌────────────────────────────────────────────────────────────────┐
│                    INPUT: Artigo ou Mensagem                      │
└────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                             │
         ▼                                             ▼
┌─────────────────────┐                     ┌─────────────┐
│ SCIENTIFIC COMPILER  │                     │ IR À ESCOLA │
│ (stage 1-12)        │                     │ (loop)      │
├─────────────────────┤                     ├─────────────┤
│ Stage 1-4: Parse    │                     │ Gap Detect  │
│ Stage 5-7: Extract │                     │ Search     │
│ Stage 8: Graph      │                     │ Synthesize │
│ Stage 9: Lint       │                     │ Save      │
│ Stage 10-12: Report │                     │           │
└─────────────────────┘                     └─────────────┘
         │                                             │
         └────────────────────┬────────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │    MEMPALACE         │
                    │  (persistence)       │
                    └─────────────────────┘
```

---

## Teste

```bash
# Teste Ir à Escola
cd /home/rodolfo/src/grilo-falante-skill
python3 -m app.services.ir_a_escola

# Teste Scientific Compiler  
python3 -m app.services.scientific_compiler
```

---

*Integrado: 2026-04-13*