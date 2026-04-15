# Promoção Formal — Especificação Completa

## Version
v2.5.0

## Status
NORMATIVO

---

## 1. Definição

**Promoção** é o processo formal pelo qual um artefacto transitа de um estado de exploração ou desenvolvimento para um estado de **canonicidade** dentro do regime Grilo Falante.

Uma vez promovido, um artefacto:
- Torna-se parte do núcleo oficial de conhecimento
- Pode ser referenciado como fonte autoritativa
- Está sujeito a regras de alteração mais rigorosas

---

## 2. Estados

### 2.1 Estados de Ciclo de Vida

| Estado | Descrição |
|--------|-----------|
| `BRUTO` | Resultado inicial, não processado |
| `EM_REVISAO` | Submetido a auditoria/validação |
| `CANDIDATO` | Aprovado pelo Lint mas não promovido |
| `PROMOVIDO` | Aceite no núcleo canónico |
| `BLOQUEADO` | Rejeitado ou needs revision |

### 2.2 Estados de Promoção

| Estado | Significado |
|--------|-------------|
| `ACCEPT` | Aprovado para promoção |
| `CONDITIONAL` | Aprovado com requisitos adicionais |
| `REJECT` | Não aprovado (não pode ser promovido) |

---

## 3. Critérios de Promoção

### 3.1 Critérios Obrigatórios (MUST)

Para ser promovido, um artefacto DEVE satisfazer:

1. **GF-ID presente** — O artefacto tem um identificador único GF-ID
2. **GMIF classificado** — O artefacto tem classificação GMIF (M1-M7)
3. **Lint Cognitivo APROVADO** — Passou em todas as verificações de lint
4. **Auditoria Hostil completada** — Não há finding CRITICAL não resolvidos
5. **Fonte rastreável** — O conteúdo pode ser rastreado a fontes

### 3.2 Critérios Condicionais (SHOULD)

1. **Não contradição sistémica** — Não invalida cápsulas já promovidas
2. **Dependências resolvidas** — Todas as dependências estão promovidas ou em estado compatível
3. **Duplicação excluída** — Não existe artefacto equivalente já promovido

### 3.3 Critérios Opcionais (MAY)

1. **Documentação completa** — Metadados e explicações presentes
2. **Testes passing** — Testes automáticos existentes e passing

---

## 4. Processo de Promoção

### 4.1 Pipeline de Promoção

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE DE PROMOÇÃO                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SUBMETER                                                 │
│     │                                                         │
│     ▼                                                         │
│  2. AUDITORIA_HOSTIL                                         │
│     │                                                         │
│     ├─── CRITICAL findings? ──▶ BLOQUEADO                    │
│     │                                                         │
│     ▼                                                         │
│  3. LINT_COGNITIVO                                           │
│     │                                                         │
│     ├─── Falha? ──▶ RETORNAR PARA REVISÃO                    │
│     │                                                         │
│     ▼                                                         │
│  4. VERIFICAÇÃO_DEPENDÊNCIAS                                 │
│     │                                                         │
│     ├─── Dependências não promovidas? ──▶ CONDITIONAL         │
│     │                                                         │
│     ▼                                                         │
│  5. AVALIAÇÃO_GMIF                                          │
│     │                                                         │
│     ├─── M4 (Doubtful)? ──▶ REJECT                          │
│     │                                                         │
│     ▼                                                         │
│  6. DECISÃO                                                  │
│     │                                                         │
│     ├─── ACEITE ──▶ PROMOVIDO                                │
│     │                                                         │
│     └─── CONDCIONAL ──▶ PROMOVIDO_COM_RESSALVAS              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Papéis

| Papel | Responsabilidade |
|-------|------------------|
| `AUTOR` | Submeter artefacto para promoção |
| `AUDITOR` | Executar auditoria hostil |
| `LINT` | Executar lint cognitivo |
| `PROMOTER` | Decidir sobre promoção |

### 4.3 Gates de Promoção

| Gate | Verificação | Estado resultante |
|------|-------------|-------------------|
| G1 | Auditoria Hostil | EM_REVISAO → CANDIDATO |
| G2 | Lint Cognitivo | CANDIDATO → ACEITE/REJECT |
| G3 | Verificação GMIF | ACEITE → PROMOVIDO |
| G4 | Revisão humana | CONDITIONAL → PROMOVIDO |

---

## 5. Revogação de Promoção

### 5.1 Motivos de Revogação

Um artefacto PROMOVIDO pode ser revogado se:

1. **Contradiação descoberta** — Nova evidência contradiz o artefacto
2. **Inconsistência sistémica** — Artefacto causa inconsistências com outros
3. **Erro de processo** — Promoção foi feita semsatisfazer critérios
4. **Obsolescência** — Conteúdo foi substituído por versão mais recente

### 5.2 Processo de Revogação

1. AuditoriaHostil identifica problema
2. Finding CRITICAL registrado
3. Decisão de revogação tomada pelo PROMOTER
4. Estado alterado para BLOQUEADO
5. Dependências notificadas
6. Registo no ledger

---

## 6. Regra de Ouro

> **Nenhum resultado é promovido sem aprovação do Lint Cognitivo.**
>
> Promoção indevida aborta o ciclo e pode invalidar artefactos dependentes.

---

## 7. Estados Proibidos

Os seguintes estados NUNCA devem ocorrer:

- `REJECT` para artefacto já usado como dependência
- `PROMOVIDO` sem GF-ID
- `PROMOVIDO` com GMIF = M4 (Doubtful)
- `CONDITIONAL` sem lista de ressalvas documentada

---

## 8. Registo

Todas as promoções e revogações são registadas no `ledger/ledger.json`:

```json
{
  "type": "promotion",
  "artefact_id": "GF-260415-M7-abc123",
  "from_state": "CANDIDATO",
  "to_state": "PROMOVIDO",
  "timestamp": "2026-04-15T10:00:00Z",
  "promoter": "system",
  "gates_passed": ["G1", "G2", "G3"]
}
```

---

## 9. Relacionamento com Outros Documentos

- `contracts_promotion.md` — Contrato base de promoção
- `system/CHECKLIST_DE_INTEGRIDADE.md` — Checklist de promoção
- `ledger/ledger.json` — Registo de todas as promoções

---

*Especificação de Promoção Formal — Grilo Falante v2.5.0*