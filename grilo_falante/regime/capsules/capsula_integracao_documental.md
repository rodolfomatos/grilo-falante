# Grilo Falante — Cápsula de Integração Documental
## Metadados Epistémicos

- **GF-ID:** GF-260415-M7-9068d3
- **GMIF:** M7 — Synthesis - aggregated from multiple derived claims
- **Gerado:** 2026-04-15T14:33:26Z
- **Fonte:** grilo_falante_capsula_de_integracao_documental.md

---


## 0. Estatuto
Documento-sombra canónico que materializa **todo o conteúdo discutido neste chat**, preservando conclusões, decisões, distinções conceituais e propostas operacionais. Este documento é **normativo**, versionável e auditável. Tem precedência interpretativa sobre notas soltas.

---

## 1. Âmbito dos Documentos Analisados
Foram integrados, de forma crítica e cruzada:
- *Everything is Context: Agentic File System Abstraction for Context Engineering*
- *Adaptation of Agentic AI* (taxonomia A1/A2/T1/T2)
- *AI Meets Brain: Memory Systems from Cognitive Neuroscience to Autonomous Agents*
- *Foundations of Large Language Models*
- *Deep sequence models tend to memorize geometrically; it is unclear why*

A análise adotou **Duplo Feynman**:
1) explicação simples (intuição),
2) explicação técnica rigorosa (leitura hostil).

---

## 2. Tese Convergente
O problema central dos LLMs e sistemas agentivos **não é capacidade cognitiva**, mas sim **governação do contexto e da memória**.

Todos os textos convergem para a necessidade de:
- externalizar contexto,
- tornar explícita a memória,
- governar adaptação,
- impedir inferência implícita não auditável.

---

## 3. Arquitetura Lógica do Grilo Falante (Filesystem Cognitivo)

O Grilo Falante é formalizado como um **filesystem lógico governado**, inspirado no paradigma “everything is a file”.

```
/grilo/
  /rules/        # regras normativas e princípios éticos
  /protocols/    # protocolos canónicos (E, C, D, etc.)
  /sources/      # fontes externas imutáveis
  /analysis/     # inferências transitórias (scratchpad)
  /verdicts/     # conclusões validadas, mas revisáveis
  /ledger/       # decisões finais (append-only)
```

### Regras estruturais
- `/sources/` é imutável.
- `/analysis/` é descartável.
- `/verdicts/` pode ser revisto.
- `/ledger/` é permanente e auditável.

Toda operação cognitiva é uma **leitura, escrita ou promoção explícita** entre paths.

---

## 4. Regime de Adaptação Aceite

Adota-se exclusivamente o paradigma **T2 — Tool Adaptation supervisionada pelo agente**.

### Implicações
- O **agente não aprende**.
- As **ferramentas cognitivas** (protocolos, critérios, filtros) é que evoluem.
- Não há fine-tuning, RL implícito ou aprendizagem paramétrica invisível.

Aprendizagem = alteração de regras, nunca de pesos.

---

## 5. Memória como Ciclo Governado

Inspirado em neurociência e agentes:

| Função Cognitiva | Path |
|------------------|------|
| História (imutável) | `/sources/` |
| Scratchpad | `/analysis/` |
| Memória ativa | `/verdicts/` |
| Verdade persistente | `/ledger/` |

### Regra forte
> Nada entra no `/ledger/` sem **verificação** e **validação** explícitas.

Esquecimento é deliberado:
- apagar `/analysis/`,
- rever `/verdicts/`,
- nunca apagar `/ledger/`.

---

## 6. Defesa contra Memória Geométrica

Assume-se explicitamente que **inferências geométricas implícitas** (embeddings, analogias globais, intuições latentes) são:
- não auditáveis,
- potencialmente ilusórias,
- epistemicamente perigosas.

### Política
- Prioridade a memória **associativa verificável**.
- Exigir sempre ancoragem textual e rastreável.
- Bloquear conclusões baseadas apenas em “estrutura global percebida”.

O Grilo Falante é **anti-geométrico por princípio**.

---

## 7. Distinção Canónica

### Verificação ≠ Validação
- **Verificação**: conformidade com a fonte.
- **Validação**: coerência com o sistema de regras.

Pipeline obrigatório:
1. Verificar
2. Validar
3. Promover (se aplicável)

---

## 8. O que é Explicitamente Rejeitado

- Aprendizagem implícita do agente (A1/A2)
- Memória que “evolui sozinha”
- Contextos não versionados
- Decisões sem ledger
- Inferência não justificável

---

## 9. Estatuto Final

Este documento constitui:
- uma **cápsula conceptual**,
- um **objeto digital governado**,
- um **documento-sombra** reutilizável.

Qualquer extensão futura do Grilo Falante deve:
- referenciar este documento,
- declarar desvios explicitamente,
- manter rastreabilidade.

---

## 10. Mantra Operacional

> “Como é que se sabe que aquilo que se pensa que se sabe é verdade?”

Este princípio governa todo o sistema.

---

## 11. Integração Canónica: LMQL — Prompt como Programa

### 11.1 Identificação do Artefacto

O documento **“Prompting Is Programming: A Query Language for Large Language Models” (LMQL)** é reconhecido como **artefacto técnico fundador** para a formalização do conceito de *Prompt Programável Governado*.

LMQL demonstra que:
- um prompt pode ser tratado como **programa executável**;
- a geração pode ser **governada em tempo de execução**;
- validação pode ocorrer **durante** a inferência, e não apenas após.

### 11.2 Princípios Extraídos

Do LMQL são integrados no Grilo Falante os seguintes princípios:

1. **Prompt ≠ Texto**  
   Prompt é um artefacto computacional com semântica, estado e controlo.

2. **Inferência Governada**  
   A geração é sujeita a invariantes explícitas, aplicadas token a token.

3. **Falha Legítima**  
   A impossibilidade de gerar output válido é um resultado aceitável.

4. **Separação de Responsabilidades**  
   O modelo gera; o sistema governa.

Estes princípios são considerados **canónicos** no regime Grilo Falante.

---

## 12. Distinção Formal: Prompt Engineering vs Prompt Programming

### 12.1 Prompt Engineering (Rejeitado)

- Texto estático ou semi‑estruturado
- Heurísticas implícitas
- Validação pós‑hoc
- Ênfase em estilo e persuasão
- Sucesso medido por fluidez

### 12.2 Prompt Programming (Adotado)

- Prompt como programa
- Variáveis, loops, condições
- Validação durante a execução
- Ênfase em correção e admissibilidade
- Sucesso medido por verificabilidade

> O Grilo Falante **opera exclusivamente** no paradigma de *Prompt Programming*.

---

## 13. Novo Artefacto Canónico: Prompt Programável Governado (PPG)

### 13.1 Definição

Um **Prompt Programável Governado (PPG)** é um prompt que:
- é executável;
- possui invariantes explícitas;
- pode interagir com ferramentas externas;
- pode falhar sem produzir output;
- é versionado e auditável.

### 13.2 Estrutura Lógica

```
/ppg/
  /prompt/        # corpo declarativo
  /constraints/   # invariantes formais
  /control/       # loops, branching, chamadas
  /validation/    # critérios de aceitação
  /trace/         # rasto de execução
```

---

## 14. Regra Normativa Fundamental

> **É proibido promover para `/ledger/` qualquer inferência produzida por prompts não‑governados.**

Apenas inferências resultantes de PPGs válidos podem ser consideradas para promoção.

---

## 15. Proposta Derivada: Grilo Prompt Language (GPL)

### 15.1 Objetivo

A **GPL** é uma linguagem conceptual (não necessariamente implementada) que formaliza:
- prompt como programa;
- governação explícita;
- distinção entre verificação e validação;
- integração ética por defeito.

### 15.2 Diferença face ao LMQL

| LMQL | GPL |
|----|----|
| Técnico | Normativo + Técnico |
| Foco em eficiência | Foco em correção e ética |
| Sound but incomplete | Conservador por defeito |
| Uso geral | Uso governado |

A GPL **não substitui** LMQL — declara as condições sob as quais LMQL (ou equivalente) é admissível.

---

## 16. Estatuto Final da Integração

Com esta secção, ficam materializados:
1. A integração formal do LMQL no Grilo Falante;
2. A distinção explícita entre Prompt Engineering e Prompt Programming;
3. A definição do Prompt Programável Governado;
4. A proposta conceptual da Grilo Prompt Language.

Este documento passa a conter a **posição oficial** do Grilo Falante sobre prompting, programação e governação cognitiva.

