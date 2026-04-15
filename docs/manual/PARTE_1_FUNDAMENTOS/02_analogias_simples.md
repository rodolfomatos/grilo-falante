# 2. Analogias Simples

## Para Entender o Grilo Falante

Pensa no Grilo Falante como um **sistema imunitário** para o teu conhecimento. Tal como o sistema imunitário ataca vírus e bactérias, o Grilo Falante ataca **afirmações falsas ou não verificadas**.

---

## Analogia 1: O Médico Detetive

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Quando vais ao médico:                                     │
│                                                             │
│  1. O médico pergunta: "O que sentiste?"                   │
│  2. O médico examina: "Há provas disso?"                   │
│  3. O médico diagnóstica: "É isto ou aquello?"             │
│                                                             │
│  O Grilo Falante faz o mesmo com o teu conhecimento:       │
│                                                             │
│  1. "O que afirmas?"      → Extrair claims                │
│  2. "Tens provas?"        → Classificar GMIF              │
│  3. "É contraditório?"     → Governance check              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Analogia 2: O Biblioteca

Imagina uma biblioteca onde cada livro tem uma **etiqueta de confiança**:

| Etiqueta | Significado |
|----------|-------------|
| 🟢 **Verde** | Múltiplas fontes confirmam |
| 🟡 **Amarelo** | Uma fonte, pode estar errado |
| 🟠 **Laranja** | Contradições detetadas |
| 🔴 **Vermelho** | Requer verificação urgente |

O Grilo Falante faz este labeling automático para cada claim que encontras.

---

## Analogia 3: O Aeroporto

No controlo de segurança do aeroporto:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. PASSAPORTE          → Quem és?                         │
│     └─► É o mesmo em todas as verificações?               │
│                                                             │
│  2. RAIO-X DA BAGAGEM   → O que levas?                    │
│     └─► Está tudo bem embalado?                            │
│                                                             │
│  3. ENTREVISTA           → Para onde vais?                  │
│     └─► Faz sentido a viagem?                              │
│                                                             │
│  No conhecimento:                                           │
│                                                             │
│  1. FONTE               → De onde vem?                    │
│  2. EVIDÊNCIA           → Há provas?                       │
│  3. CONSISTÊNCIA        → Faz sentido no contexto?         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Analogia 4: O Editor de Jornal

Um jornal responsável não publica tudo. Tem editores:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  REPÓRTER: "X aconteceu!"                                 │
│      │                                                     │
│      ▼                                                     │
│  EDITOR DE FACTOS: "Provas?"                              │
│      │                                                     │
│      ▼                                                     │
│  EDITOR LEGAL: "Podemos publicar?"                        │
│      │                                                     │
│      ▼                                                     │
│  CHEFE: "Está pronto?"                                    │
│      │                                                     │
│      ▼                                                     │
│  PUBLICAÇÃO                                               │
│                                                             │
│  O Grilo Falante é este editor, mas automático:           │
│                                                             │
│  REPÓRTER: A tua mensagem                                 │
│      │                                                     │
│      ▼                                                     │
│  GRILO FALANTE:                                           │
│      1. Extrai claims                                     │
│      2. Verifica fontes                                   │
│      3. Classifica GMIF                                   │
│      4. Governance check                                  │
│      │                                                     │
│      ▼                                                     │
│  OUTPUT: Claims classificadas e verificadas               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Analogia 5: O Café

Pensa no Grilo Falante como uma **máquina de café**:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ENTRADA (grão cru)                                        │
│      │                                                     │
│      ▼                                                     │
│  ┌───────────────┐                                        │
│  │ MOINHO        │  → Fragmentar (extrair claims)        │
│  └───────┬───────┘                                        │
│          │                                                 │
│          ▼                                                 │
│  ┌───────────────┐                                        │
│  │ FILTRO        │  → Classificar (GMIF)                 │
│  └───────┬───────┘                                        │
│          │                                                 │
│          ▼                                                 │
│  ┌───────────────┐                                        │
│  │ ÁGUA QUENTE   │  → Verificar (governance)              │
│  └───────┬───────┘                                        │
│          │                                                 │
│          ▼                                                 │
│  SAÍDA (café puro)                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

O café puro = conhecimento verificado
O café turvo = conhecimento misturado com falsidades
```

---

## Analogia 6: O GPS

O Grilo Falante é como um **GPS para o conhecimento**:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  GPS diz: "Aqui estás"                                     │
│      │                                                     │
│      ├──► "Para chegar lá, precisas de provas"              │
│      │                                                     │
│      ├──► "Esta estrada tem buracos (contradições)"         │
│      │                                                     │
│      └──► "Chegarás lá em X tempo (classificação)"         │
│                                                             │
│  Grilo diz: "Essa claim é M4 (duvidosa)"                  │
│      │                                                     │
│      ├──► "Precisava de mais fontes"                        │
│      │                                                     │
│      ├──► "Há contradição com Y"                           │
│      │                                                     │
│      └──► "Recomendaria verificar Z primeiro"               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Analogia 7: O Judge

Pensa num **juiz** que aplica a lei:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  JUIZ PERGUNTA:                                            │
│                                                             │
│  1. "Quais são os factos?"                                 │
│     → Extração de claims                                   │
│                                                             │
│  2. "Quem são as testemunhas?"                             │
│     → Fontes e evidências                                  │
│                                                             │
│  3. "Há contradições?"                                     │
│     → Detetar M4                                           │
│                                                             │
│  4. "Qual a sentença?"                                     │
│     → Classificação GMIF                                   │
│                                                             │
│  5. "Há precedentes?"                                     │
│     → Verificar contra grafo de conhecimento               │
│                                                             │
│  O Grilo Falante é este juiz, mas para afirmações:         │
│                                                             │
│  "O réu (claim) é culpado (M4) por falta de provas."     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Resumo Visual

```
         TU
          │
          ▼
    ┌───────────┐
    │  GRILO    │
    │  FALANTE  │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
EXTRACÇÃO   VERIFICAÇÃO
    │           │
    ▼           ▼
  CLAIMS     GMIF
    │           │
    └─────┬─────┘
          │
          ▼
    GOVERNANCE
          │
          ▼
     OUTPUT
    (verdadeiro
     ou bloqueado)
```

---

## Conclusão

O Grilo Falante pode parecer complexo, mas é como ter um **amigo muito curioso** que pergunta sempre:

- "Tens a certeza?"
- "Quem disse isso?"
- "Há provas?"
- "Não estarás a contradizer-te?"

**E isso é bom!** Porque nos ajuda a pensar melhor.

---

*Voltar ao [Índice](../00_INDICE.md)*
