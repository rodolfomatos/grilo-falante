# 1. O Que é o Grilo Falante?

## Resumo para Crianças

Imagina que tens um **amigo robô** muito especial que te ajuda a pensar.

Quando tu dizes alguma coisa, ele pergunta:
- "Tens a certeza disso?"
- "Quem te disse isso?"
- "Existem provas?"

Este robô chama-se **Grilo Falante** porque é como um grilo que faz perguntas - quer saber se as coisas são mesmo verdadeiras.

---

## Explicação para Leigos

O Grilo Falante é um **sistema de governança epistémica**. Em palavras simples:

> Ajuda-te a pensar melhor, questionando as tuas afirmações.

### O Problema que Resolve

Quando usamos ChatGPT ou outros chatbots, podemos:
- Aceptar informações falsas como verdade
- Fazer afirmações sem provas
- Confundir opinião com facto

O Grilo Falante cria **regras** para evitar isso.

---

## Analogia: O Detective

Pensa no Grilo Falante como um detective muito rigoroso:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   TU: "Os golfinhos são peixes!"                            │
│                                                             │
│   DETECTIVE GRILO:                                          │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ "Essa afirmação requer provas.                      │   │
│   │  Os golfinhos respiram ar (não têm guelras).       │   │
│   │  Têm sangue quente (não são peixes).                │   │
│   │  Recomendaria classificar como M4 (DUVIDOSO)."     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Níveis de Confiança

O Grilo Falante usa **GMIF** - um sistema de 7 níveis:

| Nível | Nome | Significado | Exemplo |
|-------|------|-------------|---------|
| M1 | **Primário** | Provas independentes confirmam | "3 estudos dizem X" |
| M2 | **Contextual** | Verdadeiro se assumires certas coisas | "Se A, então B" |
| M3 | **Parcial** | Estrutura incompleta | "A teoria sugere X" |
| M4 | **Duvidoso** | Contradições encontradas | "A diz X, B diz Y" |
| M5 | **Interpretação** | Uma fonte clara | "O IPCC diz X" |
| M6 | **Derivado** | Inferência lógica | "X segue de A e B" |
| M7 | **Síntese** | Agregado de múltiplas fontes | "Com base em 5 estudos..." |

---

## Para Que Serve?

### 1. Análise de Conteúdo

Quando lês um artigo ou relatório, o Grilo Falante pode:
- Extrair afirmações (claims)
- Classificar cada uma com GMIF
- Detetar contradições

### 2. Chat Governado

Se usares `/grilo chat`:
- Cada mensagem é analisada
- Claims são extraídas automaticamente
- Podes verificar se tens provas

### 3. Auditoria

O sistema pode fazer uma **auditoria hostil** - verificar se há problemas no teu texto ou raciocínio.

---

## Arquitetura Simplificada

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌─────────────┐                                           │
│   │   TU / LLM  │  ← Usuário                               │
│   └──────┬──────┘                                           │
│          │                                                  │
│          ▼                                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              GRILO FALANTE                          │   │
│   │                                                     │   │
│   │   1. Recebe mensagem                                │   │
│   │   2. Extrai claims (afirmações)                    │   │
│   │   3. Classifica com GMIF                           │   │
│   │   4. Verifica governança                           │   │
│   │   5. Guarda em memória                             │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│          │                                                  │
│          ▼                                                  │
│   ┌─────────────┐  ┌─────────────┐                         │
│   │  MemPalace  │  │ PostgreSQL  │  ← Memória              │
│   │  (rápido)   │  │ (definitivo)│                         │
│   └─────────────┘  └─────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Ciclo de Trabalho

O Grilo Falante funciona em **ciclos**:

```
1. CARREGAR regime    ← python3 grilo_pipeline.py
       │
       ▼
2. ACORDAR           ← Declarar intenção e tempo
       │
       ▼
3. TRABALHAR         ← Fazer queries, criar claims
       │
       ▼
4. DORMIR            ← Guardar tudo, terminar
```

---

## Quem Deve Usar?

| Pessoa | Porquê |
|--------|--------|
| **Investigadores** | Verificar afirmações em artigos |
| **Estudantes** | Aprender a pensar criticamente |
| **Developers** | Integrar governança em LLMs |
| **Jornalistas** | Verificar factos antes de publicar |

---

## Próximo Passo

Agora que sabes o que é, vamos aprender a [instalar](03_instalacao.md)!

---

*Voltar ao [Índice](../00_INDICE.md)*
