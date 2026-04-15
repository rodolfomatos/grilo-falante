# A_FAZER — Memória Insular e Sistema de Memória Contextualizada

**Estatuto:** Documento de Planeamento Consolidado
**Versão:** 1.0
**Data:** 2026-04-16
**Contexto:** Grilo Falante v3.0 — Memória Insular

---

## Nota Prévia

Este documento consolida toda a informação disponível sobre a visão do sistema de memória contextualizada do Grilo Falante. Pretende servir como base para um plano de implementação rigoroso.

信息来源:
- `/home/rodolfo/Desktop/Artigos/vamospartiraloiçatoda/new/memo_anchor_feynman_pedagogico_gf_ema_memoria_insular.md`
- `/home/rodolfo/Desktop/Artigos/documento_modelo_cognitivo_comparativo.md`
- `/home/rodolfo/Desktop/Artigos/capsula_aprendizagem_sem_memoria_e_artigos.md`
- `/home/rodolfo/Desktop/Artigos/grafo_modelo_cognitivo_canonico_v_2.md`
- `/home/rodolfo/Desktop/Artigos/A Graphical Meta-Information Framework/Modelo Gráfico de Meta-Informação.md`
- `/home/rodolfo/src/grilo_falante_v3.0/docs/06-unified-vision.md`
- Código fonte existente em `/home/rodolfo/src/grilo_falante_v3.0/`

---

# PARTE I — VISÃO E METÁFORAS FUNDAMENTAIS

## 1. O Problema de Fundo

Modelos de linguagem aparentam "aprender com erros", mas **não possuem memória normativa persistente** nem compromisso vinculativo com correções passadas. O que exibem é **adaptação contextual de curto prazo**, não aprendizagem estrutural.

A distinção fundamental é:
- **Adaptação intra-ciclo:** ajuste local durante a interação
- **Aprendizagem estrutural:** incorporação durável de correções como regras futuras

> **Tese principal:** Modelos de linguagem não aprendem; podem ser tornados aprendentes apenas por governação externa.

---

## 2. A Metáfora do Lago e das Ilhas

### 2.1 O Lago

O lago representa o campo de fundo da memória e da informação disponível. Esse lago inclui:
- conhecimento latente do modelo
- o que foi dito pelo humano
- material previamente trabalhado
- padrões ainda não explicitados
- associações difusas

**Nota Hostil:** Este lago não pode ser tratado como um todo indiferenciado. Há estatutos diferentes. O sistema deve distinguir camadas.

### 2.2 A Pedra (Saliência)

Uma interação relevante é como uma pedra que cai no lago:
- A pedra não adiciona só conteúdo
- Cria saliência
- Marca um ponto do campo como cognitivamente importante
- Algumas pedras fazem apenas ondulação passageira
- Outras, se forem suficientemente relevantes ou revisitadas, dão origem a algo mais estável

### 2.3 A Ilha (Agregado Consolidad)

Quando uma perturbação se consolida, emerge uma "ilha":
- Uma ilha não é apenas uma claim
- É um **agregado cognitivo**
- Pode conter: ideias, claims, hipóteses, premissas, decisões, documentos, ligações a fontes, exemplos, tensões internas, trabalho pendente

> Uma ilha com árvores, flores e animais: uma região de memória com ecologia interna própria.

A memória não deve ser concebida apenas como coleção de partículas isoladas, mas como **territórios semânticos habitáveis**.

### 2.4 Use It or Lose It

As ilhas também têm dinâmica temporal:
- Uma ilha muito usada pode tornar-se mais acessível, mais central, mais próxima
- Uma ilha pouco revisitada pode tornar-se mais distante, menos saliente, mais difícil de reativar

**Nota Importante:** Isto não deve significar apagamento cego. Valor epistémico e frequência de uso **não são a mesma coisa**. A erosão deve ser entendida como **redução de saliência ou prioridade de recuperação**, não como perda automática de estatuto.

---

## 3. A Diferença Entre Correção Factual e Legitimidade Epistémica

Uma resposta pode estar factual ou pragmaticamente certa por sorte, por associação ou por fluência, **sem ter ainda legitimidade epistémica suficiente**.

Legitimidade epistémica implica:
- proveniência
- ligação a evidência
- rastreabilidade
- suporte identificável
- ausência de promoção implícita
- possibilidade de auditoria

> **Acertar não basta**, se o sistema não sabe em que base está a acertar, nem permite auditar essa base.

---

## 4. O Que Significa "O Sistema Pode Ir Estudar"

Surgiu também a ideia de que o sistema, olhando para as ilhas e para as lacunas que elas contêm, pode "ir estudar".

Isto não significa absorver automaticamente tudo o que encontra. Significa algo mais governado:
- Identificar que uma ilha ou artefacto central tem lacunas
- Disparar procura orientada de bibliografia ou fontes
- Materializar fontes relevantes
- Construir documentos sombra
- Mapear cobertura, claims e contradições
- Só depois integrar isso no sistema de forma auditada

> Estudar não é consumir. É adquirir material novo sob regime controlado.

---

## 5. Aprendizagem por Delegação

Uma das ideias mais distintivas do projeto é a noção de aprendizagem por delegação:
- O modelo pode produzir sugestões, hipóteses ou material exploratório
- Mas a aprendizagem durável e governada do sistema acontece na memória externa normativa
- O que o sistema "aprende" com legitimidade não é o que o modelo simplesmente disse, mas o que foi materializado, auditado, promovido e integrado

> **O modelo executa; o regime aprende.**

---

## 6. As Três Dimensões da Memória

O método de estudo pessoais para exames revela três dimensões que o sistema também precisa de separar:

### 6.1 Cronologia
- Quando surgiu isto?
- Em que aula, dia ou sessão?

### 6.2 Ontologia
- A que tópico canónico pertence?
- Em que entrada do índice primário se insere?

### 6.3 Pragmática
- Para que pergunta, tarefa ou operação é útil?
- Como é que isto ajuda a fazer algo?

> Esta tripla separação é muito superior a guardar apenas texto ou embeddings.

---

## 7. Estruturas Propostas pelo Método de Estudo

### 7.1 Ledger Cronológico
Equivalente ao caderno por dia. Serve para captura e proveniência.

### 7.2 Índice Canónico Primário
Uma estrutura estável de tópicos do domínio. Não é improvisada a cada interação. Serve como mapa de topo.

### 7.3 Índice Operativo ou Pragmático
Uma camada de perguntas, tarefas, procedimentos e "como fazer X".

### 7.4 Coverage Map
Uma forma explícita de mapear que fontes, documentos ou artefactos cobrem determinado tópico ou pergunta.

### 7.5 Bundle de Reentrada
Quando o sistema quer responder ou estudar um problema, pode construir um pacote que reúna:
- Os tópicos certos
- As perguntas operativas certas
- Os artefactos centrais
- As claims associadas
- As fontes relevantes
- Os conflitos e lacunas existentes

---

## 8. Ciclo Dia/Noite — Dormir/Acordar

### 8.1 O "Ir Dormir" (Sanitização Batch)

O "ir dormir" é precisamente fazer a sanitização de tudo o que se passou durante "o dia":
- Processar o dia
- Agregar em torno de centros de gravidade (pedras/ilhas)
- Indexar
- Validar
- Colocar na memória persistente, devidamente trabalhada

> O ir à escola, em batch, se me faço entender.

### 8.2 O "Acordar" (Restauração de Contexto)

O "acordar" significa ir buscar o contexto sanitizado para se poder continuar num "novo dia":
- Não é apenas carregar vectors
- É restaurar o estado relevantes das ilhas
- É recarregar o contexto, não apenas os dados

---

## 9. O Que o Sistema Não É

### 9.1 Não É Um Chatbot com Memória

O sistema não deve ser confundido com:
- Um chatbot que guarda mensagens
- Uma base vetorial que faz similarity search
- Um RAG tradicional

### 9.2 Porque Não Basta Uma Vector DB

Uma vector DB é óptima para:
- Evocar semelhanças
- Aproximar conteúdos
- Sugerir candidatos de recuperação
- Reativar materiais relacionados

Mas uma vector DB, por si só, **não sabe**:
- Qual é o estatuto de um objeto
- Se algo é hipótese, claim, nota, documento, evidência ou conclusão
- Se uma coisa foi validada ou só sugerida
- Como uma ideia nasceu
- Que transformações sofreu
- Qual é a sua proveniência canónica
- Que autoridade tem no sistema

> A vector DB deve ser vista como **índice de evocação**, não como ontologia nem como fonte de verdade canónica.

### 9.3 Porque Não Basta Guardar Chats

Um chat bruto tem vários defeitos:
- Mistura sinal e ruído
- É difícil de navegar
- Não distingue o que foi importante do que foi contingente
- Não explicita estatutos epistémicos
- Não fornece uma unidade cognitiva estável para trabalho posterior

---

## 10. O Que o Sistema Deve Ser

O sistema deve materializar **artefactos cognitivos relevantes**:
- Memos
- Notas
- Cápsulas conceptuais
- Documentos sombra
- Snapshots de código
- Working sets
- Relatórios de auditoria
- Hipóteses explicadas pedagogicamente
- Propostas de arquitetura
- Eventos de promoção

> O chat é fluxo; o artefacto materializado é objeto.

---

# PARTE II — ESTADO ATUAL DO SISTEMA

## 11. O Que Existe

### 11.1 Estrutura de Diretórios

```
/home/rodolfo/src/grilo_falante_v3.0/
├── app/
│   ├── skills/
│   │   ├── chat_shell.py          # ChatShell class (incompleto)
│   │   └── grilo_falante_skill.py # Interface CLI
│   ├── data/
│   │   └── memory/
│   │       ├── semantic.py        # MemPalace integration
│   │       └── graph/            # Claims extraction
│   └── services/
│       └── pipeline.py
├── grilo_falante/
│   ├── backend/
│   │   ├── mcp/server.py         # MCP tools (40+)
│   │   ├── memory/
│   │   │   └── mempalamace_cache.py  # MemPalace cache
│   │   └── api/main.py           # REST API
│   └── regime/
│       ├── loader.py
│       ├── acordar.py
│       └── state_machine.py
├── docs/
│   └── manual/                   # 32 ficheiros de documentação
└── sessions/                     # Para guardar sessões (criado pela nova feature)
```

### 11.2 O Que Está Implementado

| Componente | Estado | Descrição |
|------------|--------|----------|
| ChatShell | Parcial | Classe criada, sessões guardadas em JSON |
| Regime (ACORDAR/DORMIR) | Parcial | Ciclo existe mas não faz sanitização batch |
| MemPalace | Parcial | Vector DB básica, guarda claims |
| GMIF | Implementado | Classificação M1-M7 |
| MCP Tools | ~40 tools | Chat, query, claims, audit |
| REST API | Parcial | Manual API + PINA endpoints |
| Chat interactivo | Parcial | `/grilo chat` funciona |

### 11.3 O MemPalace Atual

O MemPalace está em `/home/rodolfo/.mempalace/palace` com:
- ChromaDB como vector store
- Wing `wing_conversas` para chat
- Wing `wing_claims` para claims
- Fallback para memória em JSON

**Problema:** Está a funcionar como vector DB normal, não como memória insular.

---

## 12. O Ciclo Dormir/Acordar Atual

### 12.1 O Que Existe

```python
# Em chat_shell.py
async def start():
    # Loader.load() → Acordar.execute()
    pass

async def end():
    # Acordar.vai_dormir() → save()
    pass
```

### 12.2 O Que Falta

O `vai_dormir()` atual apenas:
- Faz save do estado
- Não faz sanitização
- Não agrega em torno de centros de gravidade
- Não processa batch o dia
- Não atualiza ilhas

O `acordar()` atual apenas:
- Carrega o estado guardado
- Não restaura contexto de ilhas
- Não faz reentrada por saliência

---

# PARTE III — LACUNAS IDENTIFICADAS

## 13. Lacunas da Visão vs. Implementação

### 13.1 Ontologia Nuclear

| Requisito | Estado | Gap |
|-----------|--------|-----|
| Definição formal de "Ilha" | Não existe | Uma ilha precisa de: identificador estável, artefactos fundadores, membros internos, relações com outras ilhas, grau de consolidação, score de ativação, estado atual, proveniência, histórico de reativações |
| Definição de "Pedra" | Metaórica | Precisa de tradução técnica: o que constitui saliência? |
| Definição de "Lago" | Metaórica | Precisa de especificação das camadas |
| Estatuto de artefactos | Parcial | Cápsula, Documento Sombra, Objeto Digital existem mas não têm machine de estados rigorosa |

### 13.2 Critérios de Saliência

| Requisito | Estado | Gap |
|-----------|--------|-----|
| O que faz uma pedra criar saliência? | Não definido | Quantas interações? Que tipo? |
| Quando é que uma pedra se torna ilha? | Não definido | Threshold? Critério? |
| Como se mede "relevância"? | Não implementado | Frequência? Novidade? Conexão? |
| Como se calcula "erosão"? | Não implementado | Redução de saliência vs. perda de valor |

### 13.3 Camadas de Memória

| Camada | Estado | Gap |
|--------|--------|-----|
| Campo latente do modelo | N/A | Não é memória do sistema |
| Entrada dialógica | Guardada | Não processada/sanitizada |
| Artefactos materializados | Parcial | Existem mas não têm proveniência completa |
| Estruturas formais (claims, grafos) | Parcial | GMIF existe mas não influencia-promoção |
| Índice vetorial | MemPalace | Não tem ontologia, só evocação |

**Falta:** Separação rigorosa entre camadas.

### 13.4 Ciclo Dormir/Acordar

| Fase | Estado | Gap |
|------|--------|-----|
| Coletar interações do dia | Guardado | Não agregado |
| Identificar pedras/saliências | Não | Não implementado |
| Agregar em torno de centros de gravidade | Não | Não existe conceito de centro |
| Validar/consolidar | Não | Sem processo batch |
| Indexar em ilhas | Não | Ilhas não existem |
| Guardar em memória persistente | JSON | Não é semanticamente indexado |

| Fase | Estado | Gap |
|------|--------|-----|
| Carregar contexto do último dia | Guardado | Não é contexto de ilhas |
| Restaurar estado das ilhas ativas | Não | Não existe conceito |
| Reentrada por saliência | Não | só carrega tudo |

### 13.5 Regimes de Promoção

| Requisito | Estado | Gap |
|-----------|--------|-----|
| Transições entre estatutos | Parcial | SUSPENDED → ASSERTED existe |
| Gates de promoção | Parcial | F7/F8 existem mas não usam saliência |
| Auditoria hostil | Parcial | Existe mas não é contínua |
| Rastreabilidade | Parcial | Claims têm ID mas não têm genealogia completa |

---

# PARTE IV — REQUISITOS TÉCNICOS PARA IMPLEMENTAÇÃO

## 14. Definição Técnica de "Ilha"

Uma ilha, no sistema técnico, precisa de:

```yaml
Ilha:
  identificador: string (único, estável)
  nome: string (legível)
  descrição: string

  # Fundadores
  artefactos_fundadores:
    - artefacto_id: string
      tipo: enum
      data_criação: datetime
      criado_por: session_id

  # Membros internos
  membros:
    - member_id: string
      tipo: claim | documento | nota | cápsula | ...
      saliência: float (0-1)
      data_inserção: datetime
      inserido_por: session_id

  # Relações
  relações:
    - ilha_id: string
      tipo:related_to | contradiz | complementa | ...
      força: float (0-1)

  # Dinâmica
  grau_consolidação: float (0-1)  # Quanto mais usado, mais consolidado
  score_ativação: float  # Recency × Frequência × Relevância
  estado: enum [DORMINTE, ATIVA, ERODENDO, CONSOLIDADA]

  # Proveniência
  data_criação: datetime
  histórico_reações:
    - data: datetime
      tipo: reativação | edição | consulta
      session_id: string

  # Metadados epistémicos
  claims_validadas: int
  claims_pendentes: int
  lacunas_identificadas: list[string]
```

---

## 15. Definição Técnica de "Pedra"

```yaml
Pedra:
  id: string
  tipo_interação: enum [MENSAGEM, CLAIM, DOCUMENTO, EVENTO, ...]

  # Saliência (o que fez esta pedra "bater")
  saliência:
    valor: float (0-1)
    componentes:
      frequência: float  # Quantas vezes surgiu no contexto
      intensidade: float  # Reações que gerou
      novidade: float  # Quão diferente é do que já existia
      relevância: float  # Conexão com ilhas existentes

  # Impacto
  impacto_criou_ilha: boolean
  ilha_criada: string (se aplicável)
  impacto_ilhãs_existentes:
    - ilha_id: string
      delta_saliência: float

  # Temporal
  data_criação: datetime
  última_reativação: datetime
  contagem_reações: int

  # Conteúdo
  conteúdo_original: string
  embedding: vector (1536)  # Para recuperação
```

---

## 16. Ciclo "Ir Dormir" — Especificação

```
IR_DORMIR():
  1. COLETAR interações desde último acordar
     - Mensagens
     - Claims extraídas
     - Documentos materializados
     - Eventos de promoção/bloqueio

  2. IDENTIFICAR pedras (saliências)
     - Para cada interação desde último acordar:
       - Calcular saliência
       - Se saliência > threshold_pedra:
         - Criar registo Pedra

  3. AVALIAR transformação em ilhas
     - Para cada Pedra:
       - Se saliência > threshold_ilha OU
         contagem_reações > threshold_reações:
         - Criar nova Ilha

  4. AGREGAR em torno de centros de gravidade
     - Para cada nova Pedra:
       - Encontrar Ilhas relacionadas (embedding similarity)
       - Se similaridade > threshold_agregação:
         - Adicionar como membro da Ilha
         - Atualizar score_ativação da Ilha

  5. ATUALIZAR estado das Ilhas existentes
     - Para cada Ilha:
       - Recalcular score_ativação
       - Se score_ativação diminuiu:
         - Marcar como ERODENDO
         - NÃO apagar — apenas reduzir prioridade

  6. CONSOLIDAR memória
     - Para cada Ilha com membros novos:
       - Atualizar índice canónico
       - Atualizar coverage map
       - Gerar documento de síntese (se relevante)

  7. GUARDAR em memória persistente
     - Serializar estado de todas as Ilhas
     - Guardar Pedras não convertidas
     - Atualizar ledger cronológico

  8. GERAR relatório de sono
     - Resumo: quantas pedras, quantas ilhas criadas/actualizadas
     - Lacunas identificadas
     - Recomendações para acordar
```

---

## 17. Ciclo "Acordar" — Especificação

```
ACORDAR(tarefa=None):
  1. CARREGAR estado persistente
     - Restaurar Ilhas do último dormir
     - Restaurar Pedras pendentes

  2. RESTAURAR contexto de Ilhas ativas
     - Identificar Ilhas com score_ativação > threshold_ativo
     - Carregar membros dessas Ilhas
     - Carregar histórico recente

  3. SE tarefa is not None:
     a. IDENTIFICAR Ilhas relacionadas com tarefa
        - Search por embedding da tarefa
        - Matching por índice canónico
        - Matching por índice pragmático

     b. CONSTRUIR bundle de reentrada:
        - Tópicos relevantes
        - Perguntas operativas
        - Artefactos centrais
        - Claims associadas
        - Fontes relevantes
        - Conflitos e lacunas

     c. APRESENTAR contexto ao utilizador/modelo
        - Estado das Ilhas relevantes
        - Pendências de trabalho
        - Lacunas identificadas

  4. SE tarefa is None:
     - Restaurar contexto geral
     - Apresentar estado do sistema

  5. REGISTRAR reentrada
     - Atualizar histórico_reações das Ilhas
     - Incrementar contagem_reações
     - Atualizar última_reativação

  6. RETORNAR estado restaurado
```

---

# PARTE V — ONTOLOGIA PROPOSTA

## 18. Hierarquia de Objectos

```
OBJETO_DIGITAL (raiz)
├── ARTEFACTO_COGNITIVO
│   ├── Nota
│   ├── Memo
│   ├── Cápsula Conceptual
│   ├── Documento Sombra
│   └── Proposta de Arquitectura
│
├── CLAIM
│   ├── Claim Validadas
│   └── Claim Pendentes
│
├── INTERAÇÃO
│   ├── Mensagem
│   ├── Evento
│   └── Pedido de Estudo
│
├── ILHA (agregado)
│   ├── Membros (Claims, Documentos, Notas...)
│   └── Relations (entre Ilhas)
│
└── PEDRA (saliência)
    └── Pode transitar para → ILHA
```

## 19. Estados dos Objectos

### 19.1 Estados de Claim

| Estado | Descrição |
|--------|----------|
| ESTRUTURAL | Extractada mas não classificada |
| CLASSIFICADA | Com GMIF atribuído |
| EM_ANÁLISE | Submetida a auditoria |
| VALIDADA | Aprovada por auditoria |
| REJEITADA | Bloqueada por insuficiência |
| PROMOVIDA | Elevada a evidência |

### 19.2 Estados de Ilha

| Estado | Descrição |
|--------|----------|
| EMBRIONÁRIA | Acabou de ser criada (da Pedra) |
| ATIVA | Em uso regular |
| CONSOLIDADA | Muito usada, estável |
| ERODENDO | Pouco uso, prioritária mas distante |
| DORMINTE | Longo tempo sem uso |
| PARCIAL | Contiene membros válidos e pendentes |

### 19.3 Estados de Pedra

| Estado | Descrição |
|--------|----------|
| NOVA | Acabou de ser criada |
| EM_ESPERA | Saliente mas não agregada |
| AGREGADA | Já pertence a uma Ilha |
| TRANSFORMADA | Tornou-se Ilha |

---

# PARTE VI — REGRAS DE TRANSIÇÃO

## 20. Pedra → Ilha

```
CONDIÇÕES para Pedra → Ilha:
1. saliência.valor > 0.8 E
2. (contagem_reações > 5 OU
    impacto_criou_ilha == true)
```

## 21. Claim → Validação

```
CONDIÇÕES para Claim VALIDADA:
1. gmif_level in [M1, M2, M5] E
2. Tem proveniência E
3. Passou auditoria hostil E
4. Não contradiz Claim validada existente
```

## 22. Ilha Erosão

```
A cada IR_DORMIR:
1. Para cada Ilha:
   score_ativação_novo = score_ativação_antigo × decay_factor

   SE score_ativação_novo < threshold_erosão:
     estado = ERODENDO

   SE score_ativação_novo < threshold_hibernação:
     estado = DORMINTE

NÃO APAGAR NUNCA — apenas reduzir prioridade de recuperação
```

---

# PARTE VII — PLANO DE IMPLEMENTAÇÃO (TODO)

## Fase 0: Fundamentos (Pré-requisitos)

### TODO 0.1: Definir Ontologia Nuclear
- [ ] Criar `app/ontology/ilhas.py` com classes:
  - `Ilha`
  - `Pedra`
  - `Saliência`
- [ ] Criar `app/ontology/estados.py` com enums:
  - `EstadoIlha`
  - `EstadoPedra`
  - `EstadoClaim`
- [ ] Criar `app/ontology/relacoes.py` com tipos de relação
- [ ] Definir thresholds em `config/ontologia.yaml`:
  ```yaml
  thresholds:
    pedra_saliência: 0.3
    ilha_transição: 0.8
    agregação_similaridade: 0.75
    erosão_score: 0.1
    hibernação_score: 0.01
  ```

### TODO 0.2: Criar Modelo de Dados
- [ ] Schema de base de dados para Ilhas (PostgreSQL)
- [ ] Schema para Pedras
- [ ] Schema para histórico de transições
- [ ] Script de migração

### TODO 0.3: Atualizar MemPalace
- [ ] Renomear/converter `wing_conversas` para sistema de Ilhas
- [ ] Adicionar índice por saliência
- [ ] Adicionar índice por estado
- [ ] Manter fallback para não-Ilhas

---

## Fase 1: Ciclo Dormir/Acordar Correto

### TODO 1.1: Implementar `ir_dormir()` completo
- [ ] Criar `app/regime/dormir.py`
- [ ] Implementar步骤 1-8 do IR_DORMIR
- [ ] Criar classe `ProcessadorBatch`
- [ ] Implementar cálculo de saliência
- [ ] Implementar identificação de pedras
- [ ] Implementar agregação em ilhas
- [ ] Criar relatório de sono

### TODO 1.2: Implementar `acordar()` completo
- [ ] Atualizar `app/regime/acordar.py`
- [ ] Implementar步骤 1-6 do ACORDAR
- [ ] Implementar busca por tarefa
- [ ] Implementar bundle de reentrada
- [ ] Criar classe `ContextoRestaurado`

### TODO 1.3: Integrar no ChatShell
- [ ] Atualizar `app/skills/chat_shell.py`
- [ ] Substituir `save()` por `ir_dormir()`
- [ ] Substituir `start()` por `acordar()`
- [ ] Adicionar parâmetro `tarefa` a acordar

### TODO 1.4: Criar CLI para ciclos manuais
- [ ] Adicionar comando `grilo dormir` (forçar dormir)
- [ ] Adicionar comando `grilo acordar --tarefa=X`
- [ ] Adicionar comando `grilo estado` (ver estado das ilhas)

---

## Fase 2: Sistema de Ilhas

### TODO 2.1: Implementar Gestão de Ilhas
- [ ] Criar `app/ilhas/gerenciador.py`
- [ ] Implementar `criar_ilha(pedra)`
- [ ] Implementar `adicionar_membro(ilha_id, membro)`
- [ ] Implementar `remover_membro(ilha_id, membro_id)`
- [ ] Implementar `combinar_ilhas(ilha1_id, ilha2_id)`

### TODO 2.2: Implementar Cálculo de Saliência
- [ ] Criar `app/ilhas/saliência.py`
- [ ] Implementar `calcular_frequência(interações)`
- [ ] Implementar `calcular_intensidade(eventos)`
- [ ] Implementar `calcular_novidade(conteúdo)`
- [ ] Implementar `calcular_relevância(embedding)`
- [ ] Implementar `saliência_total(componentes)`

### TODO 2.3: Implementar Dinâmica de Erosão
- [ ] Criar `app/ilhas/erosão.py`
- [ ] Implementar `decay_score(ilha, dias)`
- [ ] Implementar `verificar_estado(ilha)`
- [ ] NÃO implementar apagamento — só prioridade

### TODO 2.4: Implementar Relações entre Ilhas
- [ ] Criar `app/ilhas/relacoes.py`
- [ ] Implementar `encontrar_ilhas_relacionadas(ilha_id)`
- [ ] Implementar `calcular_similaridade(ilha1, ilha2)`
- [ ] Implementar `sugerir_agregação(pedra)`

---

## Fase 3: Cobertura, Índice e Busca

### TODO 3.1: Implementar Índice Canónico
- [ ] Criar `app/indices/canonico.py`
- [ ] Criar estrutura de tópicos do domínio
- [ ] Implementar `mapear_ilha(ilha, índice)`
- [ ] Implementar `buscar_por_tópico(tópico)`

### TODO 3.2: Implementar Índice Pragmático
- [ ] Criar `app/indices/pragmatico.py`
- [ ] Implementar `indexar_pergunta(pergunta, ilha_id)`
- [ ] Implementar `buscar_por_tarefa(tarefa)`

### TODO 3.3: Implementar Coverage Map
- [ ] Criar `app/indices/coverage.py`
- [ ] Implementar `mapear_cobertura(tópico)`
- [ ] Implementar `fontes_para_tópico(tópico)`
- [ ] Implementar `lacunas_em_tópico(tópico)`

### TODO 3.4: Implementar Bundle de Reentrada
- [ ] Criar `app/indices/bundle.py`
- [ ] Implementar `construir_bundle(tarefa)`
- [ ] Incluir: tópicos, perguntas, artefactos, claims, fontes, conflitos

---

## Fase 4: Estudo Dirigido

### TODO 4.1: Sistema de Identificação de Lacunas
- [ ] Criar `app/estudo/lacunas.py`
- [ ] Implementar `identificar_lacunas(ilha)`
- [ ] Implementar `classificar_lacuna(lacuna)`
- [ ] Implementar `priorizar_lacunas(lacunas)`

### TODO 4.2: Motor de Estudo Dirigido
- [ ] Criar `app/estudo/motor.py`
- [ ] Implementar `estudar_lacuna(lacuna)`
- [ ] Implementar `procurar_fontes(lacuna)`
- [ ] Implementar `materializar_fonte(fonte)`

### TODO 4.3: Integração com Auditoria
- [ ] Criar `app/estudo/auditoria.py`
- [ ] Implementar `auditar_fonte_materializada(fonte)`
- [ ] Implementar `integrar_se_validada(fonte)`

---

## Fase 5: Interfaces e Integração

### TODO 5.1: Atualizar MCP Tools
- [ ] Adicionar `grilo_ilhas_list`
- [ ] Adicionar `grilo_ilha_detalhes`
- [ ] Adicionar `grilo_pedras_list`
- [ ] Adicionar `grilo_dormir`
- [ ] Adicionar `grilo_acordar`
- [ ] Adicionar `grilo_estudar`
- [ ] Atualizar `grilo_export_session` para incluir ilhas

### TODO 5.2: Atualizar REST API
- [ ] Adicionar endpoints para ilhas
- [ ] Adicionar endpoint para cobertura
- [ ] Adicionar endpoint para bundles
- [ ] Atualizar manual API

### TODO 5.3: Atualizar CLI `/grilo chat`
- [ ] Adicionar comando `:ilhas` (listar ilhas)
- [ ] Adicionar comando `:estudar` (estudo dirigido)
- [ ] Adicionar comando `:cobertura` (coverage map)
- [ ] Melhorar output do `:status`

### TODO 5.4: Documentação
- [ ] Criar `docs/manual/PARTE_X_ILHAS.md`
- [ ] Criar `docs/manual/PARTE_X_ESTUDO.md`
- [ ] Atualizar índice
- [ ] Atualizar SKILL.md

---

## Fase 6: Otimização e Estabilidade

### TODO 6.1: Performance
- [ ] Otimizar cálculo de saliência (batch)
- [ ] Implementar cache de embeddings
- [ ] Lazy loading de ilhas inativas

### TODO 6.2: Testes
- [ ] Testes unitários para saliência
- [ ] Testes unitários para transição pedra→ilha
- [ ] Testes de integração para ciclos
- [ ] Testes de erosão

### TODO 6.3: Monitorização
- [ ] Logs de ciclos dormir/acordar
- [ ] Métricas de uso de ilhas
- [ ] Alertas de erosão acelerada

---

# PARTE VIII — PRIORIDADES E DEPENDÊNCIAS

## 84. Dependências entre TODOs

```
Fase 0 (Fundamentos)
  ├── TODO 0.1 (Ontologia)
  ├── TODO 0.2 (Modelo dados)
  └── TODO 0.3 (MemPalace)
       ↑
       │
Fase 1 (Ciclo Dormir/Acordar)
  ├── TODO 1.1 (ir_dormir)
  ├── TODO 1.2 (acordar)
  ├── TODO 1.3 (ChatShell)
  └── TODO 1.4 (CLI)
       ↑
       │
Fase 2 (Sistema de Ilhas)
  ├── TODO 2.1 (Gestão)
  ├── TODO 2.2 (Saliência)
  ├── TODO 2.3 (Erosão)
  └── TODO 2.4 (Relações)
       ↑
       │
Fase 3 (Índices)
  ├── TODO 3.1 (Canónico)
  ├── TODO 3.2 (Pragmático)
  ├── TODO 3.3 (Coverage)
  └── TODO 3.4 (Bundle)
       ↑
       │
Fase 4 (Estudo)
  ├── TODO 4.1 (Lacunas)
  ├── TODO 4.2 (Motor)
  └── TODO 4.3 (Auditoria)
       ↑
       │
Fase 5 (Interfaces)
  └── TODOs 5.1-5.4
```

---

## 85. Priorização Recomendada

### Alta Prioridade ( foundations)
1. TODO 0.1 - Ontologia Nuclear
2. TODO 0.2 - Modelo de Dados
3. TODO 1.1 - ir_dormir() básico
4. TODO 1.2 - acordar() básico
5. TODO 1.3 - ChatShell atualizado

### Média Prioridade ( core memory)
6. TODO 2.1 - Gestão de Ilhas
7. TODO 2.2 - Cálculo de Saliência
8. TODO 2.3 - Dinâmica de Erosão
9. TODO 0.3 - MemPalace atualizado

### Baixa Prioridade ( enrichement)
10. TODO 3.1-3.4 - Índices
11. TODO 4.1-4.3 - Estudo Dirigido
12. TODO 5.1-5.4 - Interfaces

---

# PARTE IX — ANTI-PADRÕES A EVITAR

## 86. Armadilhas Identificadas

### 86.1 Não Confundir Frequência com Valor Epistémico
> Uma ideia muito usada não é necessariamente mais válida.

### 86.2 Não Apagar por Erosão
> Reduzir prioridade ≠ apagar. O valor epistémico persiste.

### 86.3 Não Tratar Vector DB como Ontologia
> Embeddings são índice de evocação, não fonte de verdade.

### 86.4 Não Promover por Fluência
> "Soa bem" não é legitimidade epistémica.

### 86.5 Evitar Inflação Documental
> Cada novo documento deve ser testado: aumenta capacidade real ou só solenidade?

---

# PARTE X — FONTES E REFERÊNCIAS

## 87. Documentos Fonte

| Ficheiro | Descrição |
|----------|----------|
| `memo_anchor_feynman_pedagogico_gf_ema_memoria_insular.md` | Visão completa do sistema |
| `documento_modelo_cognitivo_comparativo.md` | Análise comparativa com outras arquiteturas |
| `capsula_aprendizagem_sem_memoria_e_artigos.md` | Princípios de aprendizagem por delegação |
| `grafo_modelo_cognitivo_canonico_v_2.md` | Ontologia canónica do modelo |
| `Modelo Gráfico de Meta-Informação.md` | Framework de evidência e inferência |
| `06-unified-vision.md` | Visão unificada dos 4 projetos |

## 88. Código Fonte Relevante

| Ficheiro | Relevância |
|----------|----------|
| `app/skills/chat_shell.py` | ChatShell - base para ciclos |
| `grilo_falante/backend/memory/mempalace_cache.py` | MemPalace - memória atual |
| `grilo_falante/regime/acordar.py` | Ciclo acordar atual |
| `grilo_falante/regime/loader.py` | Loader do regime |
| `app/data/memory/semantic.py` | Integração MemPalace |

---

# FEcho

## Visão Consolidada

> O GF/EMA é uma arquitetura de governação cognitiva com memória externa normativa, na qual interações salientes podem ser preservadas como artefactos cognitivos materializados, agregadas em territórios semânticos emergentes ("ilhas"), formalizadas progressivamente em claims e estruturas auditáveis, e enriquecidas por estudo dirigido, sem que fluência, proximidade vetorial ou hábito operacional possam promover implicitamente estatuto epistémico.

## Próximo Passo

Com este documento, o próximo passo é:
1. Rever e validar o plano
2. Prioritizar os TODOs
3. Começar pela Fase 0 (Fundamentos)

---

**Documento criado:** 2026-04-16
**Última atualização:** 2026-04-16
**Estatuto:** Draft para validação
