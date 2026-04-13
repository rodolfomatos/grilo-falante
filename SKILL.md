---
name: grilo_falante
description: análise epistemológica de conteúdo - GMIF classification, MemPalace persistence, GF-IDs
trigger: /grilo
---

# /grilo

Analisa qualquer input (chat, artigo, decisão) aplicando os princípios do regime Grilo Falante:
- **GMIF** para classificar claims por força epistémica
- **MemPalace** para persistir e indexar entre sessões
- **GF-IDs** como identificadores persistentes (como DOIs para claims)

## Usage

```
/grilo analyse <path>                    # analisar ficheiro ou diretório
/grilo analyze <text>                    # analisar texto direto
/grilo chat                            # iniciar sessão de chat governado
/grilo status                          # ver estado atual do skill
/grilo memory search "<query>"          # buscar no MemPalace
/grilo memory list                    # listar wings disponíveis
/grilo export GF-XXXXXX              # exportar claim específica
/grilo graph <gf-id>                  # mostrar grafo de uma claim
```

## O Que Este Skill Faz

O Grilo Falante skill resolve três problemas:

1. **O LLM não guarda memória entre sessões** - tudo desaparece quando o chat acaba
2. **O LLM não sabe a força epistémica do que diz** - "é possível que" vs "há evidência que X"
3. **Não há rastreabilidade** - como llegó a esta conclusão?

Este skill:
- Aplica GMIF para classificar cada claim
- Guarda tudo no MemPalace (ChromaDB local)
- Gera GF-IDs únicos e persistentes

## O Que Deve Fazer

Se não sabes a resposta, diz "não sei" - não inventes.

Se tens uma hipótese, classifica-a como **M6** (Derived) ou **M3** (Partial).
Apenas **M1** ou **M5** são afirmações com base.

O skill NUNCA produz decisão - apenas análise e materialização.

## Installation

O skill automaticamente configura MemPalace na primeira utilização:
- Wing: `wing_grilo_falante` (regime)
- Wing: `wing_conversas` (suas conversas)
- Wing: `wing_artigos` (artigos analisados)

## Quick Start

```
/grilo analyze "A educação em Portugal tem três níveis: básico, secundário e superior."
```

Output:
```
GF-260412-M1-A7B3C2
├── Claim: "A educação em Portugal tem três níveis"
├── Type: M1 (Primary Evidence)
├── Verificação: Artigo 73º da Constituição
└── Context: sistema educativo português
```

## GMIF Categories

| Code | Name | Description | Requires |
|------|------|------------|----------|
| M1 | Primary Evidence | Múltiplas fontes, alta confiança | 2+ fontes |
| M2 | Contextual Condition | Com suposições | validação |
| M3 | Partial | Não classificado | investigação |
| M4 | Doubtful | Contradições detetadas | resolução |
| M5 | Interpretation | Base clara | verificação |
| M6 | Derived | Derivado de outros | rastreabilidade |
| M7 | Synthesis | Agregado final | componentes |

## Perguntas a Fazer

Antes de qualquer análise, responde:
1. **O que é o objeto?** (chat? artigo? decisão?)
2. **Qual é o objetivo?** (auditar? preservar? continuar?)
3. **Quem é o responsável?** (human-in-the-loop)

Sem estas respostas, a análise é inválida.

## Evitar

- Não faças afirmações M1/M5 sem fonte
- Não ignores contradições (classifica como M4)
- Não mantenhas contexto "no cabeça" - guarda tudo
- Não skipping fases - segue o pipeline

## Quando Falhar é Correto

Se não consegues verificar, BLOCK como **M3** ou **M4**.
Falhar é legítimo - não inventes.