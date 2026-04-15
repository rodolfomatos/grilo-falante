# 04. Primeiro Ciclo

## O Teu Primeiro Ciclo

Vais criar o teu primeiro ciclo do Grilo Falante!

---

## O Que Vais Fazer

1. Iniciar o regime
2. Declarar a tua intenção
3. Fazer uma query simples
4. Ver como o sistema classifica
5. Terminar o ciclo

---

## Passo 1: Iniciar Chat

```bash
cd ~/src/grilo_falante_v3.0
python3 -m app.skills.grilo_falante_skill chat
```

**Output esperado:**

```
============================================================
GRILO FALANTE - CHAT GOVERNADO
============================================================

> _
```

---

## Passo 2: Carregar Regime

```
> grilo_load()
{"success": true, "cycle_id": "CYCLE-260415-abc123", "state": "LOADED"}
```

**O que aconteceu:**
- Regime carregado
- Ciclo criado com ID único
- Estado mudou para LOADED

---

## Passo 3: Acordar

```
> grilo_acordar(temporal_anchor="2026-04-15", intention="Aprender a usar o Grilo Falante")
{"success": true, "state": "GOVERNING", "intention_declared": "Aprender a usar o Grilo Falante"}
```

**O que aconteceu:**
- Declaraste quando e porquê
- Regime está agora em modo GOVERNING
- Todas as tuas mensagens serão analisadas

---

## Passo 4: Faz uma Afirmação

```
> A temperatura global aumentou 1.1°C desde 1880.
[{'fact': 1}] OK. 1 claims extraídas.
```

**O que aconteceu:**

```
1. Sistema recebeu a tua mensagem
2. Extraiu a claim: "A temperatura global aumentou 1.1°C desde 1880"
3. Classificou como M5 (fonte única)
4. Guardou em memória
5. Respondeu OK
```

---

## Passo 5: Faz outra Afirmação

```
> Esta informação está correta porque o IPCC reportou.
[M5] OK. 1 claims extraída.
```

**Agora tens 2 claims guardadas.**

---

## Passo 6: Faz uma Afirmação Duvidosa

```
> Obviamente, o aquecimento global é causado pelo CO2.
[M4: DUVIDOSO] Mensagem contém claims bloqueantes.
- Blocking pattern: "obviamente"
Esta claim não será incorporada até verificação.
```

**O que aconteceu:**
- Sistema detetou palavra bloqueante "obviamente"
- Classificou como M4 (duvidoso)
- Bloqueou até verificação humana

---

## Passo 7: Ver Estado

```
> :status
{"session_id": "chat_260415_xxx", "state": "GOVERNING", "messages_count": 4, "claims_count": 2}
```

---

## Passo 8: Terminar

```
> :quit
Sessão terminada. Claims guardadas: 2
```

**O que aconteceu:**
- Regime hibernou
- Claims guardadas em MemPalace e PostgreSQL
- Ciclo fica disponível para retomar

---

## Parabéns!

Acabaste o teu primeiro ciclo!

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ✓ Regime carregado                                        │
│  ✓ Acordar executado                                        │
│  ✓ Claims extraídas e classificadas                         │
│  ✓ Governance gate aplicado                                 │
│  ✓ Ciclo terminado                                         │
│                                                             │
│  Podes continuar para aprender mais!                        │
│                                                             │
│  Próximos passos:                                          │
│  - Tenta mais queries                                       │
│  - Explora PINA                                           │
│  - Usa REST API                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## O Que Aprendeste

| Conceito | O Que Viste |
|----------|-------------|
| **LOAD** | Iniciar regime |
| **ACORDAR** | Declarar intenção |
| **Claims** | Afirmações extraídas |
| **GMIF** | Classificação M1-M7 |
| **Governance** | Verificação automática |
| **Blocking** | Palavras que requerem prova |

---

## Próximo Passo

Agora que completaste o primeiro ciclo, explora:

- [Regime Lifecycle](05_regime_lifecycle.md) - Mais sobre estados
- [Chat Governado](06_chat_gobernado.md) - Mais sobre chat
- [Claims e GMIF](08_claims_gmif.md) - Mais sobre classificação

---

*Voltar ao [Índice](../00_INDICE.md)*
