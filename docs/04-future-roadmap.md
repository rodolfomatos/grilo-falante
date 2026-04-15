# Roadmap — Ideias Futuras

## Visão

O grilo-falante-skill como **ferramenta de análise** está funcional. Para se tornar uma **implementação do regime**, precisa de evolução significativa.

---

## Implementado: State Machine (v1)

O skill agora suporta execution governed por state machine:

```bash
# Usar grafo g7 (modelo v7)
python3 grilo_pipeline.py ./app --graph g7_grilo_falante_cognitive_model_v7

# Usar g8 (modelo completo)
python3 grilo_pipeline.py ./app --graph g8_grilo_falante_unified_cognitive_model

# Usar g9 (arquitetura)
python3 grilo_pipeline.py ./app --graph g9_grilo_falante_unified_architecture
```

Os grafos são carregados de `graphs/` ou de ambrosio_v2.5.0.

### Estados processados

| Fase | Descrição | Handler |
|------|-----------|---------|
| F_M1 | Artifacts | Logging |
| F0 | Intention/Context | Registra contexto |
| F1 | Interpretation | Executa graphify |
| F15 | Claim Classification | Logging |
| F2 | Inference (Risk) | Classifica GMIF |
| EXPLORATION_CONTROL | - | Logging |
| F3 | Structuring | LLM se ativo |
| F4 | Cognitive LINT | Verifica M4 |
| VALIDATION_QUEUE | - | Logging |
| VALIDATION_TIERS | - | Logging |
| F5 | Re-execution | Logging |
| F6 | Human Validation | Store (se ativo) |
| EVIDENCE | - | Logging |
| VERIFY | - | Logging |
| CONFIDENCE | - | Logging |
| F7 | Promotion Gate | PROMOTE/BLOCK |
| F8 | Persistence | Export HTML/JSON |

---

## Curto Prazo (1-2 semanas)

### FASE 1: Estabilização

1. **GMIF avançado** — Integrar epistemic-score do EMA
   - Usar `evidence_engine.py` para calcular scores
   - Usar `gmif_graph_builder.py` para classificação real
   - Adicionar consideração de fontes, contradições, temporal validity

2. **Cache semantics** — Melhorar caching
   - Não re-extrair se não mudou
   - Invalidar por timestamp vs por hash de conteúdo

3. **Logging estruturado** — Melhorar logs
   - JSON estruturado
   - Níveis: DEBUG, INFO, WARN, ERROR
   - Output para file + stdout

### FASE 2: Integração ChatGPT

1. **Melhorar action.yaml**
   - Adicionar mais endpoints
   - Suporte a streaming
   - Documentação OpenAPI

2. **Instruções detalhadas**
   - Exemplos de uso
   - Limites definidos
   - Erros comuns

---

## Médio Prazo (1-3 meses)

### FASE 3: Regime Completo

1. **ACORDAR ritual**
   ```
   Input: { "data": "2026-04-12", "intencao": "Analisar klaim X" }
   Output: regime_ativo = true ou BLOCK
   ```

2. **Estados de Legitimidade**
   ```
   LEGITIMACY_SUSPENDED  → default
   LEGITIMACY_ASSERTED   → após accept humano
   ```

3. **Classes de Artefactos**
   - Adicionar campo `artefact_type` ao output
   - Implementar transições: Sombra → Digital → Cápsula

4. **Graph-Based Governance**
   - Quando extrai, associar a grafo usado
   - Declarar explicitamente: "Baseado no grafo gX, estado Y"
   - Validar transições antes de progredir

5. **Lint Cognitivo**
   - Após análise, verificar:
     - ACCEPT: pronto para usar
     - CONDITIONAL: precisa revisão
     - REJECT: não válido
     - REEXECUTE: tentar novamente

6. **BLOCK behavior**
   - Se transição inválida, bloquear e explicar porquê

### FASE 4: PINA Protocol

1. Identificar normas no texto
2. Suspender reasoning dependente
3. Pedir decisão humana (accept/reject/defer)
4. Guardar decisão

---

## Longo Prazo (3-6 meses)

### FASE 5: Arquitetura Completa

1. **Memória persistente** — PostgreSQL + pgvector
   - Buscar por similaridade
   - Guardar claims com estados

2. **Dashboard completo**
   - Visualizar grafos
   - Verificar claims
   - Histórico de decisões

3. **Integração ambrosio_v2.5.0**
   - Executar INSTALLER antes
   - Usar LOADER para ativar
   - Resolver via KERNEL

4. **Multi-modal input**
   - PDF, texto, código, imagens
   - Extracção de klaim de cada tipo

---

## Ideias Experimentais

### 1. Auto-Documentation

O skill gera documentação automaticamente:
- README.md para projetos
- docs/ com análises
- Changelog automático

### 2. Claim Tracking

Sistema que segue klaim ao longo do tempo:
- Quando foi criado
- Quando foi verificado
- Quando foi contradito

### 3. Collaborative Mode

Múltiplos humanos verificando insieme:
- Partilhar análises
- Votar em claims
- Discussão estruturada

### 4. Export Standards

Exportar para formatos padronizados:
- RDF/OWL para triplos
- Markdown estruturado
- LaTeX para papers

---

## Priorização Sugerida

| Fase | Impacto | Esforço | Prioridade |
|------|---------|---------|------------|
| GMIF avançado | Alto | Médio | 1 |
| ACORDAR ritual | Alto | Baixo | 2 |
| Graph governance | Alto | Médio | 3 |
| Lint Cognitivo | Alto | Baixo | 4 |
| BLOCK behavior | Médio | Baixo | 5 |
| PINA | Médio | Alto | 6 |
| PostgreSQL | Alto | Alto | 7 |

---

## Tensão: Simplicidade vs Complitude

O regime é complexo. O skill é simples.

**Opções:**

1. **Manter simples** — ferramenta de análise, não regime completo
2. **Adicionar gradual** — fase por fase, como definido acima
3. **Separar** — skill simples + addon para regime completo

**Recomendação:** Opção 2 — adicionar gradualmente, mantendo backwards compatibility.

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Complexidade excessiva | validar cada fase antes de continuar |
| Regime nunca completa | focar em valor atual + incremental |
| Dependência EMA | manter fallback se EMA mudar |
| Performance | benchmarking em cada fase |