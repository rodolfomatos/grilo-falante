# Design Principles and Architecture

## 1. Arquitetura Conceitual

O Grilo Falante v3.0 é baseado na metáfora do Rosebud do filme Citizen Kane, onde o contexto dá significado ao conhecimento.

### 1.1 ILHA — Momento-Espaço-Tempo
- **Definição:** Agregado cognitivo que representa um momento completo no tempo e espaço com participantes
- **Componentes:** Momento (timestamp), Espaço (localização), Tempo (ntp_timestamp), Participantes, Tópico, Tipo de interação, PEDRAs (contextos reutilizáveis)

### 1.2 PEDRA — Contexto Reutilizável
- **Definição:** Agregador flexível de contextos epistémicos que pode conter ShadowDocuments, DigitalObjects, ConceptualCapsules ou estar vazia
- **Componentes:** IDs únicos, timestamps de início/fim, resumo do conteúdo, listas de sombras e objetos digitais, nível GMIF, saliência, nível de consequência, histórico de reutilização

### 1.3 ShadowDocument — Sombra de uma Fonte
- **Definição:** As claims que ficam quando se consome uma fonte (como lembrar de um livro sem ter o livro físico)
- **Componentes:** Nome da fonte, tipo, referência, claims extraídas, nível de evidência, assumptions, riscos, explicações Feynman (para crianças e peritos), gaps do loop Feynman

### 1.4 DigitalObject — Entidade Referenciável
- **Definição:** Referência a objetos digitais como PDFs, URLs, imagens, arquivos
- **Componentes:** ID, tipo, referência (URL/path), título, flag de cápsula, escopo da cápsula, interpretação, efeito normativo

### 1.5 ConceptualCapsule
- **Definição:** Um DigitalObject validado que representa síntese de conhecimento
- **Estrutura:** <C, A, Σ, Δ> (Content, Scope, Interpretation, Normative Effect)

## 2. GMIF — Sistema de Classificação
- **Definição:** Grilo Falante Meaning Interpretation Framework para classificação epistémica
- **Níveis:** M1 (Proved true) a M8 (Counterfactual) com exemplos específicos
- **Importância:** O GMIF History registra o "quando" das classificações - não muda, só rastreia

## 3. Ciclos Autónomos

### 3.1 ACORDAR / IR DORMIR
- **Mecanismo:** Decisão autônoma baseada em sinais de "cansaço"
- **Sinais:** memory_load, error_rate, gaps_detected, time_since_sleep
- **Limiares:** DORMIR se sleep_score > 50, ACORDAR se wake_score > 50

### 3.2 ESCOLA
- **Definição:** Processo de resolver gaps identificados através de pesquisa e validação

## 4. Shadow First — Metodologia
- **Princípio:** Antes de perguntar, assumir, ou implementar, pesquisar documentação primeiro
- **Passos:** 
  1. Pesquisar documentação existente
  2. Criar Shadow Document
  3. Gerar FAQ
- **Regras de Ouro:**
  1. Nunca perguntes o que podes pesquisar
  2. Nunca assumas o que não documentaste
  3. Shadow debt não perdoa - cria o doc
  4. FAQ não é para ti - é para saberes o que perguntar
  5. Relatório é para o teu EU futuro
  6. Documenta tudo sempre
  7. Memória é contextual

## 5. Arquitetura de Sistema (Deployment Vision)

### 5.1 Arquitetura Sistema Completo
- **Cliente:** OpenCode com interface MCP
- **Servidor:** Docker container com:
  - FastAPI REST API (porta 8001)
  - Gerenciamento de ILHA/PEDRA
  - Servidor MCP com 40+ tools para OpenCode
  - PostgreSQL opcional (futuro)
- **Comunicação:** HTTP/REST entre OpenCode e servidor

### 5.2 Fluxo de Dados
1. OpenCode cria ILHA para a sessão
2. Ao encontrar conceito novo: adicionar ShadowDocument
3. Ao criar PEDRA: adicionar à ILHA atual
4. Ao reutilizar PEDRA noutra ILHA: atualizar campo reused_in
5. Ao fechar sessão: sync opcional para MemPalace

### 5.3 Camadas de Armazenamento
- **Primária:** JSON (data/ilhas.json) - ILHAs/PEDRAs
- **Secundária:** MemPalace - busca verbo e semântica
- **Terciária:** PostgreSQL - dados relacionais (futuro)
- **Quartenária:** Sistema de ficheiros - documentos, relatórios

## 6. Princípios de Design da Interface

### 6.1 Tomada de Decisão Consciente
- O sistema não toma decisões, apenas torna visível o custo epistemico
- Requer envolvimento humano explícito para afirmações de legitimidade
- Fornece trilhas de auditoria verificáveis para toda a produção de conhecimento

### 6.2 Clareza sobre Incerteza
- Usa GMIF para comunicar níveis de confiança epistémica
- Distingue entre diferentes tipos de conhecimento (M1-M8)
- Torna explícitas as assumptions e limitações

### 6.3 Reutilização Contextual
- Permite reutilização de PEDRAs entre ILHAs diferentes
- Mantém histórico de onde contextos foram aplicados
- Respeita que o mesmo claim pode ter significados diferentes em contextos distintos

## 7. Requisitos Não-Funcionais de Design

### 7.1 Robustez
- Graceful degradation quando componentes opcionais indisponíveis
- Persistência essencial para evitar perda de conhecimento
- Fallbacks para serviços externos (MemPalace, PostgreSQL)

### 7.2 Transparência
- Toda saída tem rasto verificável
- Estados de legitimidade claros (SUSPENDED vs ASSERTED)
- Protocolos explícitos para validação e incorporação normativa

### 7.3 Extensibilidade
- Arquitetura modular para adicionar novos tipos de análise
- Suporte a múltiplos backends de LLM (Ollama, IAEDU, OpenWebUI, OpenAI, Anthropic)
- Desenhado para integração com outras sistemas de conhecimento