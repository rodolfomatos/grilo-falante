# RFC 028: Arquitetura Híbrida Grilo Falante + AutoMem

**RFC:** 028
**Título:** Proposta de Arquitetura Híbrida com AutoMem como Camada Opcional de Recall
**Status:** Draft
**Data:** 2026-04-16
**Autores:** Análise Comparativa
**Versão:** 1.0

---

## 1. Sumário

Este RFC propõe uma arquitetura híbrida que adiciona AutoMem como camada opcional de recall ao Grilo Falante, mantendo todos os sistemas existentes como authoritative.

---

## 2. Motivação

### 2.1 Problema Atual

O sistema de recall do Grilo Falante usa:
- MemPalaceCache (ChromaDB) para fast recall
- pgvector para similarity search
- HybridRetriever com 65% semantic + 35% epistemic

Este sistema é funcional mas tem limitações:
- Sem Bridge Discovery (encontrar conexões multi-hop)
- Sem 9-componente scoring sofisticado
- Sem enrichment automático

### 2.2 Solução Proposta

Adicionar AutoMem como **camada opcional de cache** sem substituir nada.

---

## 3. Arquitetura Proposta

### 3.1 Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSULTA                                │
└─────────────────────┬───────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │ (optional - env flag)
        ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 1: AutoMem Adapter (NOVO - opcional)             │
│  • FalkorDB: Graph relationships                        │
│  • Qdrant: Vector similarity                           │
│  • Bridge Discovery: multi-hop connections               │
│  • 9-component scoring                                 │
│  • Entity Enrichment                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ (cache hit)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 2: MemPalace (MANTER)                           │
│  • ChromaDB: Fast recall (~10ms)                       │
│  • Wings: ilhas, pedras, claims                         │
│  • Ciclo dormir/acordar                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ (cache miss)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 3: PostgreSQL (MANTER - AUTHORITATIVE)         │
│  • Claims: GMIF classification                         │
│  • Graph: L1-L8 integrity checks                      │
│  • PINA: NCA decisions                                │
│  • Auditoria Hostil                                   │
└──────��──────────────────────────────────────────────────────┘
```

### 3.2 Fluxo de Dados

```python
async def query_with_automem(query: str, limit: int = 10):
    # CAMADA 1: AutoMem (se enabled)
    if settings.AUTOMEM_ENABLED:
        automem_results = await automem.recall(query, limit)
        if automem_results:
            # Verificar GMIF nos resultados
            for result in automem_results:
                await apply_gmif_classification(result)
                await apply_graph_lint(result)
                await apply_pina_filters(result)
            return automem_results
    
    # CAMADA 2: MemPalace (fallback)
    mempalace_results = await mempalace.recall(query, limit)
    if mempalace_results:
        return mempalace_results
    
    # CAMADA 3: PostgreSQL (authoritative)
    pg_results = await postgresql.query(query, limit)
    return pg_results
```

---

## 4. Especificação de Componentes

### 4.1 AutoMemAdapter (Novo)

```python
class AutoMemAdapter:
    """Adapter para integrar AutoMem como camada opcional."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.falkordb = None  # FalkorDB client
        self.qdrant = None    # Qdrant client
    
    async def recall(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[RecallResult]:
        """Recall multi-componente via AutoMem."""
        pass
    
    async def bridge_discovery(
        self,
        start_ilha_id: str,
        max_hops: int = 3
    ) -> List[Ilha]:
        """Descobrir conexões multi-hop entre ilhas."""
        pass
    
    async def enrich(
        self,
        memory_id: str
    ) -> Dict:
        """Extrair entidades automaticamente."""
        pass
    
    async def consolidate(
        self,
        memories: List[str]
    ) -> List[Cluster]:
        """Executar ciclo de consolidação."""
        pass
```

### 4.2 Configuração

```python
# settings.py
class Settings(BaseModel):
    AUTOMEM_ENABLED: bool = False
    FALKORDB_URL: str = "http://localhost:8001"
    QDRANT_URL: str = "http://localhost:6333"
    
    # Dual-write mode
    DUAL_WRITE: bool = False  # escrever em ambos
    
    # Scoring weights
    AUTOMEM_WEIGHT: float = 0.3  # peso se dual-write
    MEMPALACE_WEIGHT: float = 0.3
    POSTGRES_WEIGHT: float = 0.4
```

---

## 5. Modos de Operação

### 5.1 Modo 1: Grilo Falante Only (Padrão)

```
CONSULTA → MemPalace → PostgreSQL → (GMIF/PINA/Lint)
```

Ativado quando: `AUTOMEM_ENABLED=False`

### 5.2 Modo 2: Híbrido (Dual-write)

```
CONSULTA → AutoMem + MemPalace → (merge scores) → PostgreSQL
```

Ativado quando: `AUTOMEM_ENABLED=True AND DUAL_WRITE=True`

### 5.3 Modo 3: AutoMem-first (Cache)

```
CONSULTA → AutoMem → (se miss) → MemPalace → PostgreSQL
```

Ativado quando: `AUTOMEM_ENABLED=True AND DUAL_WRITE=False`

---

## 6. Migração

### 6.1 Fase 1: Adapter (MVP)

Criar `AutoMemAdapter` que:
- Expõe interface similar ao MemPalace
- São conecta automaticamente se AutoMem disponível
- Fallback transparente se não disponível

### 6.2 Fase 2: Dual-write (Opcional)

- Escrever em ambos sistemas simultaneamente
- Usar apenas se `DUAL_WRITE=True`

### 6.3 Fase 3: Bridge Discovery (Opcional)

- Expor ferramenta MCP para encontrar conexões multi-hop
- Mapear para o sistema de ilhas existente

---

## 7. Decisões de Arquitetura

### 7.1 Não Substituir

| Componente | Decisão |
|-----------|---------|
| MemPalace | MANTER — integrar com ilhas/pedras |
| PostgreSQL | MANTER — authoritative |
| GMIF/PINA/Graph Lint | MANTER — governância |

### 7.2 Adicionar

| Componente | Decisão |
|-----------|---------|
| AutoMem | ADICIONAR como opcional |
| FalkorDB | Usar se disponível |
| Qdrant | Usar se disponível |

### 7.3 Backward Compatibility

```python
# settings padrão
AUTOMEM_ENABLED = False  # não quebra nada

# se enabled mas não conecta, fallback automático
```

---

## 8. Riscos e Mitigações

| Risco | Mitigação |
|------|-----------|
| Complexidade | AutoMem é opcional (default: off) |
| Performance | Dual-write apenas se configurado |
| Consistency | PostgreSQL continua authoritative |
| Availability | Fallback automático |

---

## 9. Critérios de Sucesso

- [ ] AutoMemAdapter implementado
- [ ] Modo-only funciona com existing MemPalace
- [ ] Dual-write funciona se enabled
- [ ] Bridge discovery exposto como ferramenta MCP
- [ ] Backward compatibility mantida

---

## 10. Timeline

| Fase | Descrição | Prioridade |
|------|----------|-----------|
| 1 | Adapter MVP | Alta |
| 2 | Dual-write | Média |
| 3 | Bridge Discovery | Baixa |

---

## 11. Referências

- Análise Comparativa: `docs/reference/ANALISE_COMPARATIVA_AUTOMEM_VS_GRILO_FALANTE.md`
- AutoMem: https://github.com/verygoodplugins/automem
- MCP-AutoMem: https://github.com/verygoodplugins/mcp-automem

---

## 12. Histórico de Mudas

| Versão | Data | Mudança |
|--------|------|---------|
| 1.0 | 2026-04-16 | Versão inicial draft |