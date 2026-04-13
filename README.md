# Grilo Falante Skill — Documentação Completa

## 1. VISÃO DO PROJETO

### 1.1 Para Que Sirve (Versão Simples)

O Grilo Falante é um sistema que ajuda a pensar melhor sobre qualquer assunto.

Imagina que tens um amigo que nunca aceita uma ideia sem perguntar: *"De onde sabes isso? Tens provas?"*

Esse amigo é o Grilo Falante.

---

### 1.2 Visão Detalhada

O Grilo Falante é um **regime de governação cognitiva assistida** que:

1. **Extrai conceitos** de código ou documentos (como um bibliotecário)
2. **Classifica** cada conceito por quão certo parece (GMIF M1-M7)
3. **Guarda** tudo em memória para pesquisa futura
4. **Gera identificadores únicos** (GF-IDs) para cada conceito

---

## 2. REQUISITOS

### 2.1 Requisitos Funcionais

| ID | Requisito | Descrição |
|----|----------|----------|
| RF-01 | Extrair conceitos | Usar graphify para extrair nós e arestas |
| RF-02 | Classificar GMIF | Classificar por M1-M7 |
| RF-03 | Gerar GF-IDs | Criar identificadores únicos |
| RF-04 | Guardar memória | Persistir em MemPalace |
| RF-05 | Pesquisar | Buscar conceitos guardados |
| RF-06 | Output JSON | Exportar grafo annotado |

### 2.2 Requisitos Não-Funcionais

| ID | Requisito | Critério |
|----|----------|--------|
| RNF-01 | Portabilidade | Funciona em Python 3.9+ |
| RNF-02 | Latência | < 30s para 100 ficheiros |
| RNF-03 | Dependências | graphify + MemPalace (opcional) |
| RNF-04 | Fallback | Funciona sem dependências externas |

---

## 3. ARQUITETURA

### 3.1 Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    GRILO FALANTE SKILL                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT: path ou texto                                           │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────┐                                        │
│  │ 1. Extract    │ ← graphify (extrai nós + arestas)       │
│  │    (graphify) │                                        │
│  └─────────────────┘                                        │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────┐                                        │
│  │ 2. Classify  │ ← GMIF (M1-M7)                    │
│  │    GMIF     │                                        │
│  └─────────────────┘                                        │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────┐                                        │
│  │ 3. Store     │ ← MemPalace ou JSON              │
│  │    Memory   │                                        │
│  └─────────────────┘                                        │
│    │                                                        │
│    ▼                                                        │
│  OUTPUT: grafo + GF-IDs + MemPalace                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Ficheiros do Projeto

```
grilo-falante-skill/
├── grilo_pipeline.py        # Executável principal
├── api.py                # FastAPI para ChatGPT
├── chatgpt_action.yaml     # OpenAPI schema
├── chatgpt_instructions.md  # Instruções GPT
├── app/
│   ├── data/memory/graph/
│   │   ├── gmif.py
│   │   ├── claims.py
│   │   └── builder.py
│   └── skills/
└── pyproject.toml
```

---

## 4. GMIF — O Sistema de Classificação

### 4.1 O Que É (Explicação de Feynman)

**Feynman para uma criança:**
Quando somebody says algo, podes perguntar: "Tens a certeza?"

- Se essa pessoa mostra many many provas → **M1** (muito certo)
- Se mostra só uma prova → **M5** (certeza mediana)
- Se não mostra provas → **M3** (não sabes)
- Se shows duas provas que contradizem → **M4** (uidado!)

**Feynman para especialista:**
GMIF é uma taxonomia epistemológica baseada em força de evidência:
- M1: Multiple EXTRACTED sources
- M2: Assumptions present
- M3: No evidence
- M4: Contradictions detected
- M5: Clear single source
- M6: Derived from inference
- M7: Aggregated synthesis

### 4.2 tabela de Cores

| Type | Cor | Significado | Ação |
|------|-----|-----------|------|
| M1 | Verde | Muitas provas | Usar com confiança |
| M2 | Amarelo | Com suposições | Requer validação |
| M3 | Laranja | Sem provas | Investigar mais |
| M4 | Vermelho | Contradições | NÃO usar |
| M5 | Verde claro | Uma prova clara | Usar com cuidado |
| M6 | Azul | Derivado | Ver proveniência |
| M7 | Roxo | Síntese | Ver componentes |

---

## 5. GF-ID — Identificador Único

### 5.1 Formato

`GF-{YYMMDD}-{TYPE}-{HASH}`

Exemplo: `GF-260412-M1-authmo`

- GF: Prefixo Grilo Falante
- 260412: Data (12 Abril 2026)
- M1: Tipo GMIF
- authmo: Primeiros 6 caracteres do ID

---

## 6. PLATAFORMAS SUPORTADAS

### 6.1 OpenCode

**Ficheiro:** `~/.config/opencode/skills/grilo_falante/SKILL.md`

**Invocação:** `/grilo <path>`

### 6.2 ChatGPT

**Ficheiros:**
- `chatgpt_action.yaml` (OpenAPI schema)
- `chatgpt_instructions.md` (Instruções)

**Setup:**
1. Criar Custom GPT
2. Adicionar Actions com o schema YAML
3. Colar as instruções

### 6.3 Standalone

```bash
python3 grilo_pipeline.py <path>
```

---

## 7. ANÁLISE HOSTIL — ERROS E OMISSÕES

### 7.1 Problemas Identificados

| # | Problema | Severidade | Impacto |
|---|---------|-----------|--------|
| 1 | graphify pode dar timeout em large corpus | Alta | Não completa |
| 2 | MemPalace pode não estar instalado | Média | Fallback mas sem persistência |
| 3 | GH-IDs podem ter hash curto (cols) | Baixa | IDs duplicados |
| 4 | Sem sistema de "desbloqueio" | Alta | Usuário fica preso |
| 5 | GMIF usar só edge types é simplista | Média | Classificação imprecisa |
| 6 | Sem integration com ambrosio docs | Alta | Regime não executa |
| 7 | Sem validação humana integrada | Alta | Usuário non sabe se certo |

### 7.2 O Que Falta

1. **_TIMEOUT handling** — graphify pode ficar preso
2. **Retry logic** — se algo falha, tentar novamente
3. **Human-in-the-loop** — não há verificação humana
4. **Ambrosio integration** — regime não executa
5. **Grafo visual** — não há HTML exportado
6. **Cache semantics** — re-extract é sempre completo

### 7.3 O Que Não Deve Estar Aqui

1. Lógica de validação de verdade (não é competência)
2. Decisões automáticas (só analiza)
3. Acesso a bases de dados externas
4. Autenticação complexa

---

## 8. TESTES E VALIDAÇÃO

### 8.1 Testes Unitários

| Teste | Entrada | Saída Esperada |
|-------|--------|--------------|
| GMIF M1 | edge EXTRACTED | gmif_type = M1 |
| GMIF M4 | edge AMBIGUOUS | gmif_type = M4 |
| GMIF M3 | no edges | gmif_type = M3 |
| GF-ID format | node_id | GF-YYMMDD-TYPE-xxxx |

### 8.2 Teste End-to-End

```bash
cd /home/rodolfo/src/grilo-falante-skill
python3 grilo_pipeline.py ./app --no-store
```

**Esperado:**
- Extrai conceitos
- Classifica GMIF
- Output JSON

---

## 9. INSTALAÇÃO

### 9.1 Dependências

```bash
pip install graphifyy      # Extração
pip install mempalace    # Memória (opcional)
pip install fastapi uvicorn  # API (opcional)
```

### 9.2 Sem Dependências

O sistema funciona sem elas — usa fallback JSON.

---

## 10. USO

### 10.1 Linha de Comandos

```bash
# Analisar diretório
python3 grilo_pipeline.py ./src

# Apenas extrair (sem guardar)
python3 grilo_pipeline.py ./docs --no-store

# Ajuda
python3 grilo_pipeline.py --help
```

### 10.2 API

```bash
# Iniciar servidor
python3 api.py

# Testar
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"path": "./app"}'
```

---

## 11. CHATGPT — SETUP

### 11.1 Criar Custom GPT

1. Vai a chatgpt.com > Create
2. Nome: "Grilo Falante"
3. Instruções: copia de `chatgpt_instructions.md`
4. Actions: importa `chatgpt_action.yaml`
5. Save

### 11.2 Testar

- "Analisa a pasta src"
- "O que sabes sobre autenticacao?"

---

## 12. EXEMPLOS

### 12.1 Exemplo de Output

```json
{
  "total_nodes": 186,
  "total_edges": 222,
  "gmif_distribution": {
    "M1": 81,
    "M3": 105
  },
  "gf_ids": [
    "GF-260412-M1-authmo",
    "GF-260412-M3-init"
  ]
}
```

### 12.2 Exemplo de Uso

```
Utilizador: Analisa o meu projeto
Grilo: Vou analisar o diretório./app

[Executa pipeline]

Encontrei 186 conceitos,classificados assim:
- 81 com provas (M1)
- 105 sem provas (M3)

Os mais sólidos são:
- GF-260412-M1-authmo: módulo de autenticacao
- GF-260412-M1-token: gestão de tokens

Nota: 105 conceitos precisam de verificação.
```

---

## 13. TENSÃO — LIMITES CONHECIDOS

| Tensão | PorQue | Workaround |
|-------|-------|------------|
| Large corpus | Timeout | Usar subdirectórios |
| graphify não disponível | Import error | Fallback JSON |
| MemPalace não disponível | Import error | JSON file |
| Sem verificação humana | Não há humano | Usuário verifica M4 |
| GMIF simplista | Só usa edges | Usar mais fontes |

---

## 14. REFERÊNCIAS

### 14.1 Projetos Base

- **ambrosio_v2.5.0** — Regime documentado
- **epistemic-memory-architecture** — Backend GMIF
- **graphify** — Extração de conceitos
- **MemPalace** — Memória persistente

### 14.2 Documentos Relacionados

- INSTALLER.md (regime)
- LOADER.md (ativação)
- KERNEL.md (autoridade)
- GMIF.md (classificação)

---

## 15. CHANGELOG

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-04-12 | 1.0.0 | Versão inicial |

---

## 16. LICENÇA

MIT — Rodolfo