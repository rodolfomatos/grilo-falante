# ANÁLISE HOSTIL — Conceito "Ir à Escola"

---

## Resumo (1 frase)

A ideia "Ir à Escola" é simples: quando o Grilo Falante não sabe algo, vai procurar fontes fidedignas, faz um resumo que até uma criança entende, e guarda no seu diário (MemPalace) para não esquecer.

---

## O Conceito Que Pediste

> "...qualquer discurso, qualquer interação, tem uma argumentação lógica... é a procura sistemática da verdade... construir um repositório... que permita ir procurando a informação em falta, num conceito de 'ir à escola'... se o Grilo Falante não sabe algo, procura saber, vai procurar fontes fidedignas, lê-as, faz um resumo como Feynman faria..."

### Análise Hostil

1. ** gf_scientific_compiler_v_2_spec.md NÃO EXISTE** — O documentoreferenciado não existe em todo o ambrosio. Mas o conceito faz sentido.

2. **MemPalace já existe** — Já tens o sistema de memória estruturada. Só falta conectá-lo ao loop de aprendizagem.

3. **Pedras no Lago é uma boa metáfora** — Mas precisa de contexto persistido (quem disse, quando, porquê).

4. **Síntese Feynman não estava implementada** — Agora está.

---

## Números Importantes

- Gap detector: detecta até 5 gaps por mensagem
- Active search: 3 fontes (mempalace, docs, web)
- Síntese: 2 versões (criança <50 palavras, especialista <200)
- Why loop: até 3 profundidades
- GF-ID: formato `GF-260413-ESCOLA-XXXXXXXX`

---

## Problemas Críticos

### Problema 1: Documento "scientific compiler" não existe
- O que é: pediste análise de um documento que não existe
- Porque é grave: Não há especificação formal
- Como Feynman veria: "Querias um livro que não escreveste"

### Problema 2: Loop de aprendizagem não era fechado
- O que é: sistema extrai, classifica,guarda, mas nunca vai buscar conhecimento novo
- Como Feynman veria: "É como ter uma biblioteca sem biblioteca"

### Problema 3: Síntese Feynman não existia
- O que é: Não había implementação de "explica como tens 7 anos"
- Como Feynman veria: "Sabes explicar isto ao teu avô?"

### Problema 4: Contexto perdia-se
- O que é: graphify extrai entidades, mas não guarda contexto da conversa
- Como Feynman veria: "Lembras-te de onde ouviste isto?"

---

## O Que Implementámos

### 1. Gap Detector (`app/services/gap_detector.py`)
- Extrai claims factuais de mensagens
- Detecta datas,nomes,lugares,números
- Limita a top-5 gaps

### 2. Active Search (`app/services/active_search.py`)
- 3 prioridades: mempalace → docs → web
- Timeout: 10s por fonte

### 3. Feynman Synthesize (`app/services/feynman_synthesize.py`)
- Versão criança:analogias simples
- Versão especialista: com fontes

### 4. Why Loop (`app/services/why_loop.py`)
- Perguntas até profundidade 3
- "Mas porquê?" → "E como sabemos?"

### 5. Orchestrator (`app/services/ir_a_escola.py`)
- Junta tudo
- Gera GF-ID
- Guarda no MemPalace

---

## Arquitetura

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐
│ MENSAGEM  │───▶│GAP DETECTOR│───▶│ GAPS        │
└──────────┘    └─────────────┘    └──────────────┘
                                              │
                                              ▼
                   ┌─────────────────────────────────┐
                   │     ACTIVE SEARCH              │
                   │  1. mempalace 2. docs 3.web │
                   └─────────────────────────────────┘
                                              │
                                              ▼
                   ┌─────────────────────────────────┐
                   │   FEYNMAN SYNTHESIZE             │
                   │  child │ expert                │
                   └─────────────────────────────────┘
                                              │
                                              ▼
                   ┌─────────────────────────────────┐
                   │      WHY LOOP                 │
                   │  3x "porquês?"               │
                   └─────────────────────────────────┘
                                              │
                                              ▼
                   ┌─────────────────────────────────┐
                   │      PERSIST                   │
                   │  GF-ID + MemPalace              │
                   └─────────────────────────────────┘
```

---

## Recomendações

### Acção 1: Criar Scientific Compiler Spec
```bash
# Não existe - precisa ser criado
touch gf_scientific_compiler_v_2_spec.md
```

### Acção 2: Conectar ao Pipeline Existente
```python
# No grilo_pipeline.py, adicionar:
from app.services.ir_a_escola import IrAEscolaOrchestrator
```

### Acção 3: Testar End-to-End
```bash
python3 -m app.services.ir_a_escola
```

---

## Métricas por Categoria

| Componente | Ficheiros | Status |
|-----------|----------|--------|
| gap_detector.py | 1 | ✅ |
| active_search.py | 1 | ✅ |
| feynman_synthesize.py | 1 | ✅ |
| why_loop.py | 1 | ✅ |
| ir_a_escola.py | 1 | ✅ |
| docs/IR_A_ESCOLA_CONCEITO.md | 1 | ✅ |

---

## Ficheiros Criados

1. `app/services/gap_detector.py` — 250 linhas
2. `app/services/active_search.py` — 180 linhas
3. `app/services/feynman_synthesize.py` — 150 linhas
4. `app/services/why_loop.py` — 130 linhas
5. `app/services/ir_a_escola.py` — 200 linhas
6. `docs/IR_A_ESCOLA_CONCEITO.md` — especificação completa

---

## Caso de Uso Exemplo

```
Utilizador: "Alan Turing nasceu em 1912?"

→ GAP: ["Alan Turing", "1912"]
→ SEARCH: mempalace encontra "Turing"
→ CHILD: "Alan Turing foi um homem muito inteligente..."
→ EXPERT: "Alan Mathison Turing (1912-1954)..."
→ WHY: "Mas porquê ele criou a máquina de Turing?"
→ GF-ID: GF-260413-ESCOLA-Alan T
→ STATUS: complete
```

---

*Generated: 2026-04-13*
*Analisys: Hostil*
*Concepto: "Ir à Escola"*