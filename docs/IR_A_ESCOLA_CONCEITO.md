# GRIELO FALANTE — "IR À ESCOLA"
## Sistema de Aprendizagem Autónoma com Procura de Verdade

---

##Resumo (como Feynman explicaria)

O Grilo Falante é como um estudante curioso que não tem memória.
Toda vez que fala com alguém, depois não lembra do que disse.
A ideia "Ir à Escola" é simples:
1. ** Quando o Grilo Falante não sabe algo, procura **
2. ** Lê fontes fidedignas **
3. ** Faz um resumo que até uma criança entende **
4. ** Guarda no seu diário (mempalace) para não esquecer **
5. ** Pergunta "porquê?" até perceber completamente **

É como ter um amigo que:
- Não sabe tudo (ninguém sabe)
- Mas quando não sabe, vai buscar livros, lê, e explica
- Sempre diz "não sei, mas vou descobrir"

---

## Conceito: Pedras no Lago

Imagina um lago.
Cada conversa é uma pedra que jogas.
A pedra faz ondas.

Mas ondas apagam-se.

A ideia é guardar:
- **Onde caiu a pedra** (contexto)
- **Que ondas fez** (ideias geradas)
- **O que ficou das ondas** (conhecimento Extraído)

O mempalace já faz isto com os "drawers".
O que falta é:
- Conexão com o mundo exterior (fontes)
- Capacidade de procurar ativamente
- Síntese Feynman (criança + especialista)

---

## Análise Hostil do Conceito

### Problema 1: Não há "Scientific Compiler"
O documento `gf_scientific_compiler_v_2_spec.md` **não existe**.
- Pesquisámos em todo o ambrosio: não encontrado
- O conceito existe, mas a especificação não

### Problema 2: Loop de Aprendizagem Não Fechado
O sistema atual:
- Extrai conhecimento (graphify)
- Classifica (GMIF)
- Guarda (mempalace)

Mas **nunca vai buscar conhecimento novo**.
Não há função "não sei → procura → aprende".

### Problema 3: Síntese Feynman Não Implementada
O sistema gera GF-IDs e análises, mas:
- Não explicar para crianças
- Não explicar para especialistas
- Não faz perguntas "porquê?"

### Problema 4: Contexto Perdido
O graphify extrai entidades, mas não guarda:
- Contexto da conversa original
- Perguntas feitas
- Respostas aceites/rejeitadas

### Problema 5: 20 Versões, Nenhuma Aprendizagem
O ambrosio tem v1.0.0 a v2.5.0.
Mas none dessas versões representa "aprendizagem".
São apenas revisiones, não machine learning.

---

## Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────────────┐
│                    "IR À ESCOLA" LOOP                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────────┐               │
│   │ CONVERSA │────▶│ EXTRACÇÃO │────▶│ GMIF          │               │
│   │  (input) │     │(graphify) │     │ CLASSIFICAÇÃO │               │
│   └──────────┘     └──────────┘     └──────────────┘               │
│                                                  │                │
│   ┌──────────────────────────────────────────────▼                │
│   │                    GAPS                                          │
│   │         "O que não sei e preciso saber"                          │
│   └──────────────────────────────────────────────┘                │
│                                                  │                │
│   ┌──────────────────────────────────────────────▼                │
│   │              PROCURA ATIVA                                        │
│   │    (mempalace search + web search + documents)                   │
│   └──────────────────────────────────────────────┘                │
│                                                  │                │
│   ┌──────────────────────────────────────────────▼                │
│   │           SÍNTESE FEYNMAN                                       │
│   │   "Explica como se tivesse 7 anos"                            │
│   │   "Explica como se fosses especialista"                       │
│   └──────────────────────────────────────────────┘                │
│                                                  │                │
│   ┌──────────────────────────────────────────────▼                │
│   │              PERSISTÊNCIA                                       │
│   │         (mempalace + contexto)                                │
│   └──────────────────────────────────────────────┘                │
│                                                  │                │
│                     ▼                                              │
│   ┌──────────────────────────────────────────────┐               │
│   │              PERGUNTA "PORQUÊ?"                               │
│   │      "Já percebo completamente?"                          │
│   └──────────────────────────────────────────────┘               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Requisitos

### Req 1: Detetor de Gaps
```
INPUT: Mensagem do utilizador
OUTPUT: Lista de "gaps" (coisas que não sei)

CRITÉRIOS:
- Se a resposta contém afirmações factuais (dates, names, numbers)
- E o sistema não tem esses factos no mempalace
- Então é um GAP
```

### Req 2: Buscador Activo
```
INPUT: Lista de gaps
OUTPUT: Fontes encontradas

FONTES PRIORITÁRIAS:
1. MemPalace local (mais rápido)
2. Documentos do ambrosio (fontes fidedignas)
3. Web search (fallback)
4. Wikipedia / arXiv (último recurso)

NOTA: Preferir fontes primárias, não opiniões.
```

### Req 3: Síntese Feynman
```
INPUT: Informação encontrada
OUTPUT: 2 resumos

RESUMO 1 (criança 7+ anos):
- Max 100 palavras
- Sem jargão
- Com analogias do dia-a-dia

RESUMO 2 (especialista):
- Max 500 palavras
- Com precisão técnica
- Com fontes referenciadas
```

### Req 4: Contexto Persistido
```
INPUT: Tudo
OUTPUT: MemPalace entry

ESTRUTURA:
{
  "conversation_id": "...",
  "timestamp": "...",
  "original_message": "...",
  "gaps_found": [...],
  "sources_used": [...],
  "feynman_child": "...",
  "feynman_expert": "...",
  "questions_for_deepness": [...],
  "gf_id": "GF-..."
}
```

### Req 5: Loop de "Porquês"
```
INPUT: Síntese
OUTPUT: Perguntas de follow-up

PERGUNTAS ATÉ:
- 3 iterações
- Ou "não há mais perguntas legítimas"
- Ou "preciso de mais fontes"

Cada iteração: "Mas porquê?" até chegar aaxioma ou fonte primária.
```

---

## Plano de Implementação

### Fase 1: Gap Detector (1 dia)
```python
# pseudocode
def detect_gaps(message, known_facts):
    gaps = []
    claims = extract_claims(message)
    for claim in claims:
        if not is_in_mempalace(claim):
            gaps.append(claim)
    return gaps
```

### Fase 2: Buscador Activo (2 dias)
```python
def search_gaps(gaps):
    results = []
    for gap in gaps:
        # 1. MemPalace
        mp_result = mempalace.search(gap)
        if mp_result:
            results.append(("local", mp_result))
        else:
            # 2. Docs
            doc_result = search_docs(gap)
            if doc_result:
                results.append(("docs", doc_result))
            else:
                # 3. Web
                web_result = web_search(gap)
                results.append(("web", web_result))
    return results
```

### Fase 3: Síntese Feynman (2 dias)
```python
def feynman_synthesize(results):
    all_info = concatenate(results)
    
    child_summary = simplify_for_child(all_info)
    expert_summary = make_precise(all_info)
    
    return {
        "child": child_summary,
        "expert": expert_summary
    }
```

### Fase 4: Contexto + Loop (2 dias)
```python
def ir_a_escola_loop(initial_message):
    # 1. Extrai e classifica
    gaps = detect_gaps(initial_message)
    
    # 2. Procura
    sources = search_gaps(gaps)
    
    # 3. Síntese
    synthesis = feynman_synthesize(sources)
    
    # 4. Persiste
    store_in_mempalace({
        "message": initial_message,
        "gaps": gaps,
        "sources": sources,
        "synthesis": synthesis,
        "gf_id": generate_gf_id()
    })
    
    # 5. Pergunta porquês
    questions = generate_why_questions(synthesis)
    return questions
```

### Fase 5: Integração Total (3 dias)
- Ligar ao pipeline existente
- Adicionar ao mempalace como "wing"
- Testes end-to-end

---

## Casos de Uso

### Caso 1: Conversa Normal
```
Utilizador: "Quem foi Turing?"
Gap Detector: ["Alan Turing"]
Buscador: Encontra no MemPalace local
Síntese: "Alan Turing foi um filósofo inglês..."
Resposta: Explicação Feynman
```

### Caso 2: Tema Desconhecido
```
Utilizador: "O que é consciência quântica?"
Gap Detector: ["consciousness"]
Buscador: Não encontra → Web search
Síntese: "Há debate: alguns dizem X, outros dizem Y..."
Resposta: "Não sei completamente. Há teorias rivais. A mais comum diz..."
```

### Caso 3: Informação Contraditória
```
Utilizador: "A IA vai destruir humanidade?"
Gap Detector: []
Buscador: Encontra мнsgo contraditórias
Síntese: "Há 2 posições: (1) dizem que sim, (2) dizem que não..."
Resposta: "Esta questão não tem consenso. fontes A dizem X, fontes B dizem Y..."
```

---

## Erros Antecipados e Soluções

| Erro | Causa | Solução |
|-----|------|--------|
| Too many gaps | Message contém muitos factos | Limitar a top-5 |
| No sources found | Tema invented | "Não sei, não encontrei fontes" |
| Síntese wrong | Web search inaccurate | Priorizar MemPalace |
| Loop infinito | "Porquês" forever | Max 3 iterações |

---

## Métricas de Sucesso

- [ ] Gap detector trova >80% de factos uncertaines
- [ ] Buscador encontra fontess em <5 segundos
- [ ] Síntese child é entendida por criança
- [ ] Síntese expert contém fontes
- [ ] Contexto persistido correctamente
- [ ] Loop completa em <30 segundos

---

## Ficheiros a Criar

1. `app/services/gap_detector.py` — Detector de gaps
2. `app/services/active_search.py` — Buscador activo
3. `app/services/feynman_synthesize.py` — Síntese dual
4. `app/services/why_loop.py` — Loop de "porquês"
5. `app/services/ir_a_escola.py` — Orquestrador
6. `app/integrations/mempalace_integration.py` — Melhorar

---

## Integração com Existing

O sistema actual já tem:
- `grilo_pipeline.py` — extracção + classificação
- `graphify_integration.py` — graphify wrapper
- `store_mempalace()` — persistência

O que falta:
- Gap detection
- Procura activa
- Síntese
- "Porquês" loop

---

*AUTHOR: Implementation Plan*
*DATE: 2026-04-13*
*VERSION: 1.0*