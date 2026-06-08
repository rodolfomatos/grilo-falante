# Requisitos Funcionais e Não-Funcionais

## 1. Requisitos Funcionais Atuais

### RF-01: Extracção de Conceitos
- **Descrição:** Extrair nós e arestas de código/documentos usando graphify
- **Input:** path ou texto
- **Output:** grafo com nós e arestas
- **Status:** ✅ Implementado

### RF-02: Classificação GMIF
- **Descrição:** Classificar cada conceito por nível epistémico (M1-M7)
- **Input:** grafo extraído
- **Output:** gmif_type por nó
- **Status:** ⚠️ Parcial (simplista) - Melhorar para versão avançada

### RF-03: Geração de GF-ID
- **Descrição:** Criar identificador único para cada conceito
- **Formato:** GF-YYMMDD-TYPE-xxxx (12 chars)
- **Status:** ✅ Implementado

### RF-04: Persistência
- **Descrição:** Guardar conceitos em MemPalace ou JSON fallback
- **Status:** ✅ Implementado

### RF-05: Output JSON
- **Descrição:** Exportar grafo annotado com GMIF
- **Status:** ✅ Implementado

### RF-06: HTML Export
- **Descrição:** Gerar visualização HTML com cores GMIF
- **Status:** ✅ Implementado

### RF-07: ACORDAR Ritual (CRÍTICO)
- **Descrição:** Ritual de entrada com ancoragem temporal + intenção
- **Input:** data + intenção declarada
- **Output:** regime ativado ou BLOCK
- **Prioridade:** ALTA
- **Status:** ❌ Não implementado

### RF-08: Estados de Legitimidade (CRÍTICO)
- **Descrição:** LEGITIMACY_SUSPENDED vs LEGITIMACY_ASSERTED
- **Regras:**
  - Default: SUSPENDED
  - ASSERTED exige declaração humana
- **Prioridade:** ALTA
- **Status:** ❌ Não implementado

### RF-09: Classes de Artefactos (ALTO)
- **Descrição:** Documento Sombra / Objeto Digital / Cápsula
- **Regras:**
  - Sombra: incompleto, não-promotável
  - Digital: estabilizado
  - Cápsula: validada, reutilizável
- **Prioridade:** ALTA
- **Status:** ❌ Não implementado

### RF-10: Graph-Based Governance (CRÍTICO)
- **Descrição:** Todo raciocínio ancorado a grafo materializado
- **Regras:**
  - Declarar grafo usado
  - Declarar estado atual
  - Declarar transição validada
- **Prioridade:** ALTA
- **Status:** ❌ Não implementado

### RF-11: PINA Protocol (MÉDIO)
- **Descrição:** Protocol for Normative Incorporation
- **Regras:**
  - Identificar normas
  - Suspender reasoning dependente
  - Decisão humana (accept/reject/defer)
- **Prioridade:** MÉDIA
- **Status:** ❌ Não implementado

### RF-12: Lint Cognitivo (CRÍTICO)
- **Descrição:** Verificação obrigatória de output
- **Estados:** ACCEPT | CONDITIONAL | REJECT | REEXECUTE
- **Prioridade:** ALTA
- **Status:** ❌ Não implementado

### RF-13: BLOCK Behavior (MÉDIO)
- **Descrição:** Bloquear quando transição inválida
- **Regras:** Não progredir sem validação
- **Prioridade:** MÉDIA
- **Status:** ❌ Não implementado

## 2. Requisitos Não-Funcionais Atuais

### RNF-01: Portabilidade
- **Critério:** Python 3.9+
- **Status:** ✅ Conforme

### RNF-02: Latência
- **Critério:** < 30s para 100 ficheiros
- **Status:** ⚠️ Depende de graphify

### RNF-03: Timeout
- **Critério:** 60s default, configurável
- **Status:** ✅ Implementado

### RNF-04: Retry
- **Critério:** 3 tentativas default, configurável
- **Status:** ✅ Implementado

### RNF-05: Cache
- **Critério:** Guardar resultados intermediários
- **Status:** ✅ Implementado

## 3. Requisitos Não-Funcionais do Regime

### RNF-06: Rastreabilidade
- **Critério:** Todo output deve tener rasto verificável
- **Depende:** RF-07, RF-10, RF-12

### RNF-07: Responsabilidade Humana
- **Critério:** Decisões requerem input humano explícito
- **Depende:** RF-08, RF-11

### RNF-08: Materialização
- **Critério:** Tudo que existe para o regime deve ser artefacto
- **Depende:** RF-09