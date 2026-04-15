# ANÁLISE HOSTIL — ERROS, OMISSÕES E FALHAS

## 1. ANÁLISE HOSTIL — O QUE FALTA

### 1.1 Erros Críticos

| # | Erro | Onde Ocorre | Consequência |
|---|------|-------------|-------------|
| E1 | Sem timeout handling | grilo_pipeline.py | Bloqueia para sempre |
| E2 | Sem retry logic | api.py | Uma falha = tudo parado |
| E3 | GF-ID hash curto | gmif.py |.Colisões em large corpus |
| E4 | Sem human verification | todo o sistema | Usuário non sabe se certo |

### 1.2 Omissões Críticas

| # | Omissão | PorQue Problema |
|-------|---------|-------------|
| O1 | Não executa INSTALLER.md | Regime não applied |
| O2 | Não usa LOADER.md | Regime não ativado |
| O3 | Não valida com fontes reais | GMIF usa só inferência |
| O4 | Não exporta HTML | Sem visualização |
| O5 | Não cacheia | Re-extract sempre |
| O6 | Sem logging | Não há debug |

---

## 2. ANÁLISE COMPARATIVA

### 2.1 O Que Está vs O Que Deveria Estar

| Componente | Agora | Deveria |
|-----------|-------|--------|
| **Extração** | graphify | OK |
| **GMIF** | Heurístico simples | Complexo (epistemic-architecture) |
| **Persistência** | MemPalace ou JSON | MemPalace |
| **Regime** | Não executa | INSTALLER + LOADER |
| **Visualização** | Não há | HTML com cores |
| **Verificação** | Não há | Human-in-loop |

### 2.2 Comparação com Projetos Base

| Projeto | O que tem | O que falta no Grilo |
|---------|----------|---------------------|
| **ambrosio_v2.5.0** | INSTALLER, LOADER, KERNEL | Execução real |
| **epistemic-architecture** | GMIF completo, DB | Simplicidade |
| **graphify** | Extração + HTML | classification GMIF |
| **MemPalace** | Persistence | Integração full |

---

## 3. PROBLEMAS ESPECÍFICOS

### 3.1 GMIF Simplista

**Agora:**
```python
# Só olha para edge types
if ambigous > 0: M4
elif extracted > 0: M1
elif inferred > 0: M5
else: M3
```

**Problema:** Não considera:
- Número de fontes
- Qualidade das fontes
- Contradições reais
- Temporal validity

**Melhoria:** Usar epistemic-architecture:
- `evidence_engine.py` — compute epistemic score
- `gmif_graph_builder.py` — classification real

### 3.2 GF-ID Collision

**Agora:**
```python
node_id[:6]  # Only 6 chars
```

**Problema:** Em 1000+ nodes, collisão é provável.

**Melhoria:** Usar hash completo ou UUID.

### 3.3 Sem Timeout

**Agora:**
```python
result = extract(files)  # Pode ficar preso
```

**Melhoria:**
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Extração timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60 segundos

result = extract(files)
signal.alarm(0)
```

### 3.4 Sem Retry

**Agora:**
```python
if "error" in extraction:
    return  # Fail
```

**Melhoria:**
```python
for attempt in range(3):
    try:
        result = extract(files)
        break
    except Exception as e:
        if attempt == 2:
            raise
        print(f"Retry {attempt + 1}: {e}")
```

---

## 4. QUESTÕES NÃO RESPONDIDAS

### 4.1 Quando Não Usar?

O INSTALLER.md diz:
- custo erro baixo → NÃO usar
- velocidade > rastreabilidade → NÃO usar

**Question:** O skill verifica isto?

**Resposta:** NÃO. Sempre executa.

### 4.2 Quem Verifica M4?

**Question:** Se há M4 (contradições), quem resolve?

**Resposta:** Não há mecanismo. O sistema mostra M4 mas não ajuda a resolver.

### 4.3 Como Promover Conclusões?

O regime tem "Promotion Gate" (Pipeline v3).

**Question:** O skill promove conclusão ou apenas analiza?

**Resposta:** Apenas analiza. Não promove nada.

---

## 5. MATRIZ DE RISCOS

| Risco | Probabilidade | Impacto | Severidade |
|------|--------------|---------|----------|
| Timeout | Alta | Alto | CRÍTICO |
| GF-ID collision | Média | Médio | ALTO |
| MemPalace fail | Alta | Médio | MÉDIO |
| M4 não resolvido | Alta | Alto | CRÍTICO |
| HTML não gerado | Média | Baixo | BAIXO |

---

## 6. RECOMENDAÇÕES

### 6.1 Imediatas (Fazer Agora)

1. Adicionar timeout handling
2. Adicionar retry logic
3. Usar GF-ID mais longo
4. Adicionar human verification step

### 6.2 Curto Prazo (Esta Semana)

1. Executar INSTALLER.md antes
2. Usar GMIF do epistemic-architecture
3. Gerar HTML com cores GMIF
4. Cache de extraction

### 6.3 Médio Prazo (Este Mês)

1. Integration com ambrosio docs
2. Promotion Gate real
3. Logging estruturado
4. Dashboard simples

---

## 7. CHECKLIST — IMPLEMENTAÇÃO

### 7.1 Agora (Feito)

- [x] Extracção básica
- [x] GMIF classification
- [x] GF-ID generation
- [x] MemPalace ou JSON
- [x] API FastAPI
- [x] ChatGPT action
- [x] OpenCode skill

### 7.2 Imediato (Por Fazer)

- [ ] Timeout handling
- [ ] Retry logic
- [ ] GF-ID longer
- [ ] Human verification

### 7.3 Curto (Semanas)

- [ ] GMIF advanced
- [ ] HTML export
- [ ] Cache
- [ ] Logging

### 7.4 Médio (Meses)

- [ ] INSTALLER integration
- [ ] LOADER integration
- [ ] Promotion Gate
- [ ] Dashboard

---

## 8. CONCLUSÃO

### O Que Está Bom

- Extração funciona (graphify)
- GMIF classification básica
- Portável (Python only)
- Multi-plataforma

### O Que Precisa Melhorar

- GMIF simplista (precisa epistemic-architecture)
- Não executa regime
- Sem timeout
- Sem human verification
- Sem visualização

### Frase de Feynman

> "Se não consegues explicar isto a uma criança de 6 anos, não percebeste bem. Se precisares de mais de 6 páginas, estás a complicar."

**Nossa versão:**
> "Se precisares de mais de 1 comando para analisar, está demasiado complexo."

---

*Documento gerado automaticamente. Versão 1.0.0*