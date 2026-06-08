# 11. Todas as MCP Tools

Referência completa de todas as 55+ ferramentas disponíveis via MCP.

---

## Regime Lifecycle (8 tools)

### grilo_load
Carregar o regime para iniciar um novo ciclo.

```python
grilo_load()
```

**Resposta:**
```json
{
  "success": true,
  "message": "Regime loaded successfully",
  "cycle_id": "CYCLE-260415-6f71a939",
  "state": "LOADED"
}
```

---

### grilo_unload
Terminar o ciclo atual.

```python
grilo_unload()
```

---

### grilo_acordar
Executar ritual de wake-up com âncora temporal e intenção.

```python
grilo_acordar(
    temporal_anchor="2026-04-15",
    intention="Analisar relatório Q1",
    mode="exploratory"  # ou "committed"
)
```

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| temporal_anchor | string | Data/hora (YYYY-MM-DD) |
| intention | string | O que pretendes fazer |
| mode | string | "exploratory" ou "committed" |

---

### grilo_vai_dormir
Hibernar o regime.

```python
grilo_vai_dormir()
```

---

### grilo_resume
Retomar de hibernação.

```python
grilo_resume()
```

---

### grilo_status
Obter estado atual.

```python
grilo_status()
```

**Resposta:**
```json
{
  "cycle_id": "CYCLE-260415-6f71a939",
  "state": "GOVERNING",
  "claims_count": 15,
  "nca_pending": 2,
  "is_exploratory": true
}
```

---

### grilo_health
Verificar saúde do sistema.

```python
grilo_health()
```

---

### grilo_get_ledger_stats
Estatísticas do ledger de auditoria.

```python
grilo_get_ledger_stats()
```

---

## Chat Governado (4 tools) 🆕

### grilo_chat_start 🆕
Iniciar nova sessão de chat governado.

```python
grilo_chat_start(
    session_id="opcional_id",
    temporal_anchor="2026-04-15",
    intention="Analisar relatório",
    mode="exploratory"
)
```

**Resposta:**
```json
{
  "success": true,
  "state": "GOVERNING",
  "cycle_id": "CYCLE-260415-xxx",
  "session_id": "mcp_260415_xxx",
  "active_sessions": ["mcp_260415_xxx"]
}
```

---

### grilo_chat_send 🆕
Enviar mensagem no chat governado.

```python
grilo_chat_send(
    message="As vendas aumentaram 20% no Q1.",
    session_id="mcp_260415_xxx",
    role="user"  # ou "assistant"
)
```

**Resposta:**
```json
{
  "message": "OK. 2 claims extraídas.",
  "claims_extracted": 2,
  "gmif_summary": {"fact": 1, "claim": 1},
  "governance_passed": true,
  "blocked_claims": [],
  "session_id": "mcp_260415_xxx"
}
```

---

### grilo_chat_end 🆕
Terminar sessão de chat.

```python
grilo_chat_end(session_id="mcp_260415_xxx")
```

---

### grilo_export_session 🆕
Exportar dados da sessão para resume.

```python
grilo_export_session(session_id="mcp_260415_xxx")
```

**Resposta:**
```json
{
  "script": "#!/bin/bash\n# Grilo Falante Session Resume...",
  "session_id": "mcp_260415_xxx",
  "cycle_id": "CYCLE-260415-xxx",
  "messages_count": 15,
  "claims_count": 42
}
```

---

## Query e Pesquisa (3 tools)

### gepeto_query
Executar query através do pipeline epistémico.

```python
gepeto_query(
    query="Quais são as conclusões principais?",
    session_id="default",
    auto_school_mode=True
)
```

---

### grilo_semantic_search 🆕
Pesquisa semântica rápida via MemPalace.

```python
grilo_semantic_search(
    query="mudanças climáticas",
    limit=5
)
```

**Resposta:**
```json
{
  "query": "mudanças climáticas",
  "results": [
    {"text": "...", "wing": "ambrosio", "score": -0.129},
    ...
  ],
  "count": 5,
  "source": "mempalace"
}
```

---

### grilo_generate_gfid
Gerar GF-ID para uma claim.

```python
grilo_generate_gfid(
    content="A temperatura aumentou 1.1°C",
    gmif_level="M5",
    suffix="temp"
)
```

---

## Claims (4 tools)

### gepeto_create_claim
Criar nova claim.

```python
gepeto_create_claim(
    claim_key="CLM-temp-001",
    claim_text="A temperatura global aumentou 1.1°C desde 1880",
    source_id=1,
    session_id="default",
    gmif_level="M5",
    gmif_confidence=0.7
)
```

---

### gepeto_get_claim
Obter claim por ID.

```python
gepeto_get_claim(claim_id=1)
```

---

### gepeto_validate_claim
Submeter validação de curator.

```python
gepeto_validate_claim(
    claim_id=1,
    curator_id=1,
    decision="approved",  # approved, rejected, corrected
    notes="Confirmado por múltiplas fontes",
    evaluator_confidence=0.9
)
```

---

### grilo_classify_gmif
Classificar texto com GMIF.

```python
grilo_classify_gmif(
    claim_text="A temperatura aumentou",
    source_count=1
)
```

---

## Gaps e School Mode (4 tools)

### gepeto_list_gaps
Listar gaps identificados.

```python
gepeto_list_gaps(limit=20)
```

---

### gepeto_get_gap
Obter gap específico.

```python
gepeto_get_gap(gap_key="GAP-260415-001")
```

---

### gepeto_resolve_gap
Resolver gap com claim.

```python
gepeto_resolve_gap(
    gap_key="GAP-260415-001",
    claim_key="CLM-xxx",
    resolution="Investigação adicional"
)
```

---

### gepeto_school_mode
Executar modo escola para um gap.

```python
gepeto_school_mode(
    gap_key="GAP-260415-001",
    research_depth="surface"  # surface, moderate, deep
)
```

---

## PINA Protocol (4 tools)

### grilo_pina_propose
Propor normativa.

```python
grilo_pina_propose(
    source_document="relatorio_q1.pdf",
    faithful_statement="Todas as fontes de energia devem ser renováveis",
    location="page 5, parágrafo 2",
    graph_scope="energy_policy"
)
```

---

### grilo_pina_decide
Registar decisão humana.

```python
grilo_pina_decide(
    nca_id="NCA-abc123-def456-260415",
    decision="A"  # A=Incorporar, B=Rejeitar, C=Adiar
)
```

---

### grilo_pina_status
Estado do PINA.

```python
grilo_pina_status()
```

**Resposta:**
```json
{
  "pending_candidates": 2,
  "pending_list": [...],
  "active_invariants": 5,
  "active_list": ["NCA-xxx", "NCA-yyy"]
}
```

---

### grilo_pina_pending 🆕
Listar NCAs pendentes.

```python
grilo_pina_pending(limit=20)
```

---

## Auditoria e Governance (5 tools)

### grilo_audit
Correr auditoria hostil nos claims.

```python
grilo_audit(limit=50)
```

---

### grilo_lint
Verificar texto para padrões bloqueantes.

```python
grilo_lint(text="É óbvio que isso é verdade.")
```

**Resposta:**
```json
{
  "state": "suspicious",
  "message": "Blocking patterns detected",
  "issues": ["Contém 'óbvio' - requer prova"]
}
```

---

### grilo_run_auditoria_hostil
Workflow completo de auditoria.

```python
grilo_run_auditoria_hostil(
    content="O estudo prova que LLMs são conscientes..."
)
```

---

### grilo_run_autopsia_literatura
Workflow autopsia de literatura.

```python
grilo_run_autopsia_literatura(content="[artigo completo...]")
```

---

### grilo_run_triagem
Workflow de triagem.

```python
grilo_run_triagem(content="[conteúdo a triar]")
```

---

## Grafos e Capsules (3 tools)

### grilo_validate_transition
Validar transição num grafo epistémico.

```python
grilo_validate_transition(
    from_node="node_a",
    to_node="node_b",
    graph_id="gf-001"
)
```

---

### grilo_list_graphs
Listar grafos registados.

```python
grilo_list_graphs()
```

---

### grilo_stamp_capsule
Assinar ficheiro como cápsula epistémica.

```python
grilo_stamp_capsule(
    capsule_path="/path/to/file.md",
    gmif_level="M5",
    force=False
)
```

---

## Fontes e Curadores (4 tools)

### gepeto_create_source
Criar fonte governada.

```python
gepeto_create_source(
    source_key="SRC-journal-001",
    title="Nature Climate Change",
    authors=["Smith et al."],
    year=2024,
    source_tier="peer_reviewed"
)
```

---

### gepeto_get_source
Obter fonte.

```python
gepeto_get_source(source_id=1)
```

---

### gepeto_create_curator
Criar curator.

```python
gepeto_create_curator(
    curator_key="CUR-human-001",
    name="João Silva",
    curator_type="human",
    specializations=["climate", "energy"]
)
```

---

### gepeto_get_curator
Obter curator.

```python
gepeto_get_curator(curator_id=1)
```

---

## Feynman e Learning (2 tools)

### gepeto_feynman_explain
Gerar explicação estilo Feynman.

```python
gepeto_feynman_explain(
    topic="Aquecimento global",
    level="fep1"  # fep1, fep2, fep3
)
```

---

### gepeto_session_prefs
Configurar preferências de sessão.

```python
gepeto_session_prefs(
    session_id="default",
    topics=["climate", "energy"],
    domains=["science"],
    recency_weight=0.3,
    preferred_categories=["M1", "M2", "M5", "M7"],
    auto_school_mode=True
)
```

---

## ILHA/PEDRA Memory (6 tools) 🆕

Sistema de memória contextual com persistência JSON.

### grilo_ilhas_list 🆕
Listar todas as ILHAs (memórias).

```python
grilo_ilhas_list(
    estado="ai_to_ai",  # opcional: ai_to_ai, ai_to_human, human_to_human
    limit=50
)
```

**Resposta:**
```json
{
  "ilhas": [
    {
      "id": "ILHA-20260416-143022",
      "timestamp": "2026-04-16T14:30:22Z",
      "topic": "Shadow First Methodology",
      "title": "AI-to-AI: Shadow First Methodology",
      "pedras_count": 3,
      "is_processed": false
    }
  ],
  "count": 1
}
```

---

### grilo_ilhas_get 🆕
Obter detalhes de uma ILHA.

```python
grilo_ilhas_get(ilha_id="ILHA-20260416-143022")
```

**Resposta:**
```json
{
  "ilha": {
    "id": "ILHA-20260416-143022",
    "topic": "Shadow First Methodology",
    "participants": [{"name": "grilo-gf", "role": "ai"}]
  },
  "pedras": [
    {
      "id": "PEDRA-00001",
      "content_summary": "Shadow documents capture...",
      "gmif_level": "M3"
    }
  ]
}
```

---

### grilo_pedras_list 🆕
Listar todas as PEDRAs (contextos reutilizáveis).

```python
grilo_pedras_list(limit=50)
```

---

### grilo_pedras_get 🆕
Obter details de uma PEDRA.

```python
grilo_pedras_get(pedra_id="PEDRA-00001")
```

---

### grilo_pedra_add_shadow_document 🆕
Adicionar um shadow document a uma PEDRA.

```python
grilo_pedra_add_shadow_document(
    pedra_id="PEDRA-00001",
    source_name="MemPalace README",
    source_type="document",
    source_reference="https://github.com/...",
    feynman_f1="Para crianças: é como uma biblioteca...",
    feynman_f2="Para experts: sistema de memória...",
    feynman_f3_gaps=["Como funciona a indexação?"],
    extracted_claims=["MemPalace usa ChromaDB"],
    evidence_level="complete",
    assumptions=["ChromaDB está disponível"],
    misuse_risks=["Pode ser usado para tracking"]
)
```

---

### grilo_pedra_add_digital_object 🆕
Adicionar um objeto digital (ou capsule) a uma PEDRA.

```python
grilo_pedra_add_digital_object(
    pedra_id="PEDRA-00001",
    type="pdf",
    reference="https://arxiv.org/paper.pdf",
    title="Paper sobre LLMs",
    description="Estudo sobre embeddings",
    is_capsule=False
)
```

Para criar uma **ConceptualCapsule** (síntese validada):

```python
grilo_pedra_add_digital_object(
    pedra_id="PEDRA-00001",
    type="capsule",
    reference="internal:capsule:001",
    title="Teorema da Conservação",
    is_capsule=True,
    capsule_scope="Física clássica",
    capsule_interpretation="Σ_delta",
    capsule_normative_effect="Δ_universal"
)
```

---

### grilo_pedra_update 🆕
Atualizar metadata de uma PEDRA.

```python
grilo_pedra_update(
    pedra_id="PEDRA-00001",
    content_summary="Nova descrição",
    saliencia=0.8,
    consequence_level=0.6,
    gmif_level="M4"
)
```

---

### grilo_pedra_get_content 🆕
Obter todo o conteúdo de uma PEDRA incluindo shadow documents e digital objects.

```python
grilo_pedra_get_content(pedra_id="PEDRA-00001")
```

**Resposta:**
```json
{
  "id": "PEDRA-00001",
  "content_summary": "Shadow documents capture...",
  "is_empty": false,
  "shadow_documents": [
    {
      "id": "sd-xxx",
      "source_name": "MemPalace README",
      "source_type": "document",
      "extracted_claims": ["Usa ChromaDB"],
      "evidence_level": "complete"
    }
  ],
  "digital_objects": [
    {
      "id": "do-yyy",
      "type": "pdf",
      "reference": "https://...",
      "title": "Paper",
      "is_capsule": false
    }
  ],
  "gmif_level": "M3",
  "saliencia": 0.5,
  "gmif_events": [
    {"gmif_level": "M3", "timestamp": "2026-04-16T..."}
  ]
}
```

---

## Resumo por Categoria

| Categoria | Tools |
|-----------|-------|
| **Regime** | grilo_load, grilo_unload, grilo_acordar, grilo_vai_dormir, grilo_resume, grilo_status, grilo_health, grilo_get_ledger_stats |
| **Chat** | grilo_chat_start, grilo_chat_send, grilo_chat_end, grilo_export_session, grilo_import_session |
| **ILHA/PEDRA** 🆕 | grilo_ilhas_list, grilo_ilhas_get, grilo_pedras_list, grilo_pedras_get, grilo_pedra_add_shadow_document, grilo_pedra_add_digital_object, grilo_pedra_update, grilo_pedra_get_content |
| **Query** | gepeto_query, grilo_semantic_search, grilo_generate_gfid |
| **Claims** | gepeto_create_claim, gepeto_get_claim, gepeto_validate_claim, grilo_classify_gmif |
| **Gaps** | gepeto_list_gaps, gepeto_get_gap, gepeto_resolve_gap, gepeto_school_mode, gepeto_sair_da_escola |
| **PINA** | grilo_pina_propose, grilo_pina_decide, grilo_pina_status, grilo_pina_pending |
| **Audit** | grilo_audit, grilo_lint, grilo_run_auditoria_hostil, grilo_run_autopsia_literatura, grilo_run_triagem |
| **Graph** | grilo_validate_transition, grilo_list_graphs, grilo_stamp_capsule |
| **Fontes** | gepeto_create_source, gepeto_get_source, gepeto_list_sources, gepeto_create_curator, gepeto_get_curator |
| **Learning** | gepeto_feynman_explain, gepeto_session_prefs |
| **Sleep/Wake** | grilo_dormir, grilo_acordar |

---

*Voltar ao [Índice](../00_INDICE.md)*
