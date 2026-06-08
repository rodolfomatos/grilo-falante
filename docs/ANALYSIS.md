# ANÁLISE DO PROJETO — Grilo Falante v3.0

**Data:** 2026-04-16
**Analista:** OpenCode
**Versão do documento:** 1.0

---

## 1. Resumo Executivo

Este documento analisa o estado atual do projeto Grilo Falante v3.0 comparando com a visão documentada. Identifica gaps, erros, incongruências e sugere correções.

**Conclusão principal:** O modelo de dados está correto mas há inconsistências entre a implementação e a documentação, e faltan componentes críticos para a visão de deployment.

---

## 2. Análise Comparativa

### 2.1 Modelo ILHA/PEDRA

| Aspecto | Visão | Implementação | Estado |
|---------|-------|--------------|--------|
| ILHA com timestamp NTP | ✅ | ✅ | OK |
| ILHA com participants | ✅ | ✅ | OK |
| ILHA com pedras | ✅ | ✅ | OK |
| PEDRA como agregador | ✅ | ✅ | OK |
| started_at/ended_at | ✅ | ✅ | OK |
| shadow_documents | ✅ | ✅ | OK |
| digital_objects | ✅ | ✅ | OK |
| gmif_events (timeline) | ✅ | ✅ | OK |
| saliência | ✅ | ✅ | OK |
| consequence_level | ✅ | ✅ | OK |

**Veredicto:** Modelo ILHA/PEDRA está alinhado com a visão.

### 2.2 ShadowDocument

| Aspecto | Visão | Implementação | Estado |
|---------|-------|--------------|--------|
| source_name | ✅ | ✅ | OK |
| source_type | ✅ | ✅ | OK |
| extracted_claims | ✅ | ✅ | OK |
| evidence_level | ✅ | ✅ | OK |
| assumptions | ✅ | ✅ | OK |
| misuse_risks | ✅ | ✅ | OK |
| feynman_f1 | Mencionado | ❌ | **GAP** |
| feynman_f2 | Mencionado | ❌ | **GAP** |
| feynman_f3_gaps | Mencionado | ✅ | OK |

**Veredicto:** Faltam campos Feynman F1 e F2 no modelo.

### 2.3 DigitalObject

| Aspecto | Visão | Implementação | Estado |
|---------|-------|--------------|--------|
| type | ✅ | ✅ | OK |
| reference | ✅ | ✅ | OK |
| title | ✅ | ✅ | OK |
| is_capsule | ✅ | ✅ | OK |
| capsule_scope | ✅ | ✅ | OK |
| capsule_interpretation | ✅ | ✅ | OK |
| capsule_normative_effect | ✅ | ✅ | OK |

**Veredicto:** DigitalObject está completo.

### 2.4 Ciclos Autónomos

| Aspecto | Visão | Implementação | Estado |
|---------|-------|--------------|--------|
| Sinais de cansaço | ✅ | ✅ | OK |
| Decisão DORMIR/ACORDAR | ✅ | ✅ | OK |
| Endpoint /fatigue | Mencionado | ✅ | OK |
| Endpoint /decide-autonomous | Mencionado | ✅ | OK |
| Endpoint /execute-autonomous | ✅ | ✅ | OK |

**Veredicto:** Ciclos autónomos implementados corretamente.

---

## 3. Gaps Identificadas

### 3.1 Gaps Críticas (Alta Prioridade)

| ID | Descrição | Impacto |
|----|-----------|---------|
| G13 | Sem PostgreSQL backend | Não escala |
| G14 | Sem Dockerfile | Não há deployment |
| G15 | MCP server atualizado ✅ | OpenCode pode usar |
| G16 | Sem health endpoint | Não consegue monitorizar |

### 3.2 Gaps Médias (Média Prioridade)

| ID | Descrição | Impacto |
|----|-----------|---------|
| G8 | Wiki view conexões | Não há visualização |
| G17 | Campo identity em DigitalObject | Falta campo da visão |
| G18 | Campo purpose em DigitalObject | Falta campo da visão |

### 3.3 Gaps Menores (Baixa Prioridade)

| ID | Descrição | Impacto |
|----|-----------|---------|
| G19 | Docs não têm versões | Difícil tracking |
| G20 | Sem testes automatizados | Risco de regressões |

---

## 4. Incongruências Identificadas

### 4.1 Incongruência 1: ShadowDocument vs Article ShadowDocument

**Problema:** Existem dois modelos de ShadowDocument:
- `grilo_admin/models/ilha.py:ShadowDocument` (novo, completo)
- `grilo_admin/models/article.py:ShadowDocument` (antigo, incompleto)

**Impacto:** Confusão sobre qual usar. Código antigo usa o incompleto.

**Correção:** ✅ Unificados em 2026-04-16. `ilha.py:ShadowDocument` é a base canónica. `article.py` agora usa `ArticleShadowDocument` (mantido para retrocompatibilidade com campos específicos de artigos).

### 4.2 Incongruência 2: ConceptualCapsule Separada

**Problema:** Na visão, ConceptualCapsule é um tipo de DigitalObject (`is_capsule=True`). Na implementação, existe uma classe separada `ConceptualCapsule`.

**Impacto:** Redundância. Duas formas de representar a mesma coisa.

**Correção:** Remover `ConceptualCapsule` separada, usar apenas DigitalObject com `is_capsule=True`.

### 4.3 Incongruência 3: GMIF History vs GMIF Level

**Problema:** Na visão, `gmif_events` é uma timeline que só regista "quando". Na implementação, existe também `gmif_level` simples.

**Impacto:** Não está claro se GMIF pode mudar ou não.

**Correção:** Clarificar - GMIF é classificação atual, gmif_events é histórico. GMIF não muda após classificação inicial.

### 4.4 Incongruência 4: MemPalace Service vs CLI

**Problema:** MemPalaceService tenta usar CLI masCLI interativo requer input do utilizador.

**Impacto:** Integração não funciona automatically.

**Correção:** Usar API Python do MemPalace diretamente ou subprocess com `input=""`.

---

## 5. Erros de Implementação

### 5.1 Erro 1: `mempalace_service.py` - CLI Interativo

**Ficheiro:** `grilo_admin/services/mempalace_service.py`

**Problema:** O comando `mempalace init` é interativo e requer input do utilizador.

```python
result = subprocess.run(
    ["mempalace", "init", self._palace_path],
    capture_output=True,
    text=True,
    input="\n",  # Accept defaults
)
```

**Solução:** Não chamar `mempalace init` via subprocess. Configurar manualmente se necessário.

### 5.2 Erro 2: Modelo ShadowDocument Incompleto

**Ficheiro:** `grilo_admin/models/ilha.py`

**Problema:** Os campos `feynman_f1` e `feynman_f2` estão no modelo mas não são expostos na API adequadamente.

**Solução:** Adicionar endpoints para definir F1/F2, ou remover se não são necessários.

### 5.3 Erro 3: Persistência Dependente de Caminho

**Ficheiro:** `grilo_admin/routers/ilhas.py`

**Problema:** `_get_default_storage_path()` usa `__file__` que pode variar com o contexto de importação.

**Solução:** Usar variável de ambiente ou config file para storage path.

---

## 6. Omissões

### 6.1 Omissão 1: Sem Tests

**O que falta:** Nenhum teste automatizado.

**Impacto:** Risco de regressões. Não há forma de verificar que mudanças não quebram nada.

**Recomendação:** Adicionar pytest pelo menos para modelos e endpoints críticos.

### 6.2 Omissão 2: Sem Versioning de Docs

**O que falta:** Documentos não têm versão.

**Impacto:** Difícil saber qual é a versão mais recente.

**Recomendação:** Adicionar versão no header de cada documento.

### 6.3 Omissão 3: Sem CHANGELOG

**O que falta:** Não há registo de alterações.

**Impacto:** Não se sabe o que mudou entre sessões.

**Recomendação:** Criar CHANGELOG.md e seguir conventional commits.

### 6.4 Omissão 4: Sem Docker/Deployment

**O que falta:** Não há Dockerfile ou docker-compose.

**Impacto:** Não há forma fácil de deployar.

**Recomendação:** Criar Dockerfile e docker-compose.yml (prioridade alta).

---

## 7. Recomendações de Correção

### 7.1 Correções Imediatas (Hoje)

1. ~~**Unificar ShadowDocument**~~ - ✅ Feito em 2026-04-16
2. **Remover ConceptualCapsule separada** - Usar DigitalObject com `is_capsule=True`
3. **Corrigir MemPalace CLI** - Não usar `input="\n"`
4. **Adicionar health endpoint** - `/health` já existe, verificar se funciona

### 7.2 Correções de Curto Prazo (Esta Semana)

1. ~~**Criar Dockerfile**~~ - ✅ Feito
2. ~~**Criar docker-compose.yml**~~ - ✅ Feito
3. ~~**Atualizar MCP server**~~ - ✅ Feito
4. **Adicionar tests básicos** - Para modelos

### 7.3 Correções de Médio Prazo (Este Mês)

1. **PostgreSQL backend** - Para escalabilidade
2. **Autenticação** - JWT ou similar
3. **Wiki view** - Para visualização de conexões
4. **CI/CD** - Para deploy automático

---

## 8. Plano de Ação

### Dia 1: Correções Imediatas
```
[x] Unificar ShadowDocument models ✅
[x] Remover ConceptualCapsule redundante (marcado como deprecated)
[x] Corrigir MemPalace service
[x] Verificar health endpoint
```

### Dia 2-3: Deployment ✅
```
[x] Criar Dockerfile
[x] Criar docker-compose.yml
[x] Configurar CORS para localhost
[x] Testar em Docker
```

### Dia 4-5: MCP & OpenCode ✅
```
[x] Atualizar MCP server com novas tools
[x] Configurar mcp.json
[ ] Testar com OpenCode
[x] Documentar configuração
```

### Semana 2: Estabilização
```
[ ] Adicionar pytest
[ ] Criar CHANGELOG
[ ] PostgreSQL backend (se necessário)
[ ] CI/CD pipeline
```

---

## 9. Matriz de Priorização

| Prioridade | Ação | Impacto | Estado |
|------------|------|---------|--------|
| 1 | Docker deployment | Permite uso real | ✅ Feito |
| 2 | MCP server update | OpenCode integration | ✅ Feito |
| 3 | Unificar ShadowDocument | Consistência | ✅ Feito |
| 4 | Tests | Confiança | 🔲 Parcial (13 tests) |
| 5 | PostgreSQL | Escalabilidade | 🔲 Pendente |

---

## 10. Conclusão

O projeto está em bom estado no que diz respeito ao modelo de dados. As principais lacunas são:

1. **Deployment** - ✅ Dockerfile e docker-compose.yml criados
2. **Integração OpenCode** - ✅ MCP server atualizado com tools ILHA/PEDRA
3. **Consistência** - ✅ ShadowDocument unificado
4. **Testes** - 🔲 13 tests básicos (Auth, ILHA/PEDRA, Models, Services)

**Recomendação:** Testar Docker deployment e OpenCode integration.

---

**FIM DO RELATÓRIO**
