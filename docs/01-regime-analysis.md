# Análise do Regime — system.md

## Visão Geral

O `system.md` do ambrosio_v2.5.0 define o **regime de governação cognitiva assistida** Grilo Falante. Este documento analisa os componentes canónicos e compara com a implementação atual do grilo-falante-skill.

---

## 1. Componentes Canónicos

### 1.1 INSTALLER.md (Documento Raiz)

| Conceito | Definição | Implementado no Skill? |
|----------|-----------|------------------------|
| **Regime** | Governação cognitiva, não produção de decisões | Parcial |
| **8 Princípios invariantes** | Nada implícito, fluência≠validação, promoção só com rederivação, autoridade belongs to human, falha é legítima, BLOCK é correto, Lint obrigatório, sistema segue mesmas regras | Não |
| **Regra 0** | Materialização contínua — tudo inferido deve existir como artefacto | Não |
| **Classes de artefactos** | Documento Sombra (incompleto), Objeto Digital (estabilizado), Cápsula Conceptual (validada) | Não |
| **Estados de legitimidade** | LEGITIMACY_SUSPENDED (default), LEGITIMACY_ASSERTED (exige declaração humana) | Não |
| **ACORDAR ritual** | Ancoragem temporal + declaração explícita de intenção | Não |
| **Governação por Grafos** | Todo raciocínio deve estar ancorado a grafo materializado | Não |
| **PINA** | Protocol for Normative Incorporation | Não |
| **Lint Cognitivo** | ACCEPT/CONDITIONAL/REJECT/REEXECUTE | Não |

### 1.2 LOADER.md (Ativação)

| Conceito | Implementado? |
|----------|---------------|
| `LOAD GriloFalante FROM system.md` | Não |
| Regra 3.1 (uso implica rasto) | Não |
| Regra 3.2 (proibição de uso implícito) | Não |
| BLOCK em transição inválida | Não |
| Kernel resolution | Não |

### 1.3 KERNEL.md (Autoridade)

O Kernel define quais artefactos possuem autoridade operacional durante o ciclo governado.

---

## 2. Pergunta Fundamental

O `system.md` tenta responder:

> **"Como sabemos que o que pensamos que sabemos é verdade?"**

### Resposta do Regime

1. **Nada é implícito** — tudo deve ser explícito
2. **Validação externa** — fluência não substitui evidência
3. **Materialização** — o que não existe como artefacto não existe para o regime
4. **Autoridade humana** — o humano tem autoridade factual final
5. **BLOCK é correto** — quando não há transição válida, bloqueia-se

---

## 3. Gap Analysis

| Componente system.md | Status no Skill | Gap |
|---------------------|-----------------|-----|
| Extracção (graphify) | ✅ Implementado | OK |
| GMIF classification | ⚠️ Simplista | Precisa epistemic-architecture |
| GF-ID generation | ✅ Implementado | OK |
| Persistência (MemPalace/JSON) | ✅ Implementado | OK |
| ACORDAR ritual | ❌ Não implementado | CRÍTICO |
| LEGITIMACY states | ❌ Não implementado | CRÍTICO |
| Documento Sombra / Objeto Digital | ❌ Não implementado | ALTO |
| PINA protocol | ❌ Não implementado | ALTO |
| Lint Cognitivo | ❌ Não implementado | ALTO |
| Graph-based governance | ❌ Não implementado | CRÍTICO |
| BLOCK behavior | ❌ Não implementado | ALTO |

---

## 4. Requisitos Não-Implementados

### 4.1 ACORDAR Ritual

O regime só está ativo após:
1. **Ancoragem temporal** — data/hora declarada
2. **Declaração de intenção** — o que se pretende fazer

```
ACORDAR
Data: 2026-04-12
Intenção: Analisar projeto X para verificar klaim Y
```

**No skill:** Não existe — o skill executa sem este ritual.

### 4.2 Estados de Legitimidade

```
LEGITIMACY_SUSPENDED  → default, não validado
LEGITIMACY_ASSERTED   → exige declaração humana explícita
```

**No skill:** Não existe — todos os conceitos são tratados igualmente.

### 4.3 Classes de Artefactos

| Classe | Função | No Skill |
|--------|--------|----------|
| Documento Sombra | Exploração, incompleto | ❌ |
| Objeto Digital | Estabilizado | ⚠️ Parcial |
| Cápsula Conceptual | Validada, reutilizável | ❌ |

### 4.4 PINA Protocol

Identificar normas → incorporar como regras binding → decisão humana.

**No skill:** Não existe.

### 4.5 Lint Cognitivo

Verificação obrigatória com estados: ACCEPT, CONDITIONAL, REJECT, REEXECUTE.

**No skill:** Não existe.

---

## 5. Conclusão da Análise

O grilo-falante-skill atual implementa:
- ✅ Extração de conceitos
- ✅ Classificação GMIF básica
- ✅ Identificação GF-ID
- ✅ Persistência

Mas **não implementa** o regime de governação definido em system.md.

O skill funciona como **ferramenta de análise**, não como **regime governante**.

---

## Referências

- `/home/rodolfo/src/ambrosio_v2.5.0/system.md` (linhas 25-321: INSTALLER)
- `/home/rodolfo/src/ambrosio_v2.5.0/loader/LOADER.md`
- `/home/rodolfo/src/ambrosio_v2.5.0/system/KERNEL.md`