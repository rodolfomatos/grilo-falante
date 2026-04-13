# Análise — Boole e Zeigarnik

## Objetivo

Este documento analisa dois textos fornecidos pelo utilizador como propostas de modelos cognitivos potencialmente integráveis no `grilo-falante-skill`.

Os textos são tratados como:

- artefactos conceptuais úteis;
- narrativas com valor heurístico;
- formulações com erros, exageros e omissões;
- fontes para novos módulos cognitivos do projeto.

---

## Resumo Executivo

Os dois textos apontam para duas capacidades complementares:

1. **Boole**
   Um método para decompor um domínio em proposições estruturantes, dependências, assunções, conclusões, tensões e condições de refutação.

2. **Zeigarnik**
   Um método para modelar trabalho cognitivo inacabado, loops abertos, tensão atencional, fecho confiável e custo de incompletude.

Se forem integrados corretamente, estes modelos permitem que o projeto evolua de:

> extração de claims + state machine

para:

> motor governado que estrutura fundamentos, gere incompletudes e só promove o que foi explicitamente justificado e cognitivamente fechado.

---

## Texto 1 — Boole

## Ideia Central

O texto apresenta um método de aprendizagem baseado em três movimentos:

1. identificar proposições fundacionais;
2. perguntar o que as destruiria;
3. mapear dependências, assunções, conclusões e tensões.

Isto é profundamente compatível com o regime Grilo Falante porque força:

- explicitação;
- estrutura;
- rasto argumentativo;
- teste de fragilidade;
- diferenciação entre fundamento e derivação.

---

## O que o texto oferece de útil

### 1. Extração de estrutura antes de detalhe

O insight mais forte é este:

> Antes de acumular conteúdo, convém identificar as estruturas portantes do domínio.

Isto pode ser transformado numa fase explícita do projeto:

- `foundational_propositions`
- `domain_assumptions`
- `derived_conclusions`
- `tensions`

### 2. Refutabilidade como disciplina

A pergunta “o que destruiria esta proposição?” é útil como lint epistemológico.

No projeto, isto pode tornar-se:

- condição de falsificação;
- boundary condition;
- trigger de reexecução;
- trigger de bloqueio.

### 3. Mapa de pensamento do domínio

O texto propõe um mapa relacional antes da aprendizagem detalhada. Isso encaixa diretamente em:

- grafos `.dot`;
- GMIF;
- graph governance;
- artefactos materializados.

---

## Erros, exageros e omissões no texto Boole

### Exageros

1. A anedota do estudante do MIT não tem validação no texto.
2. “Runs every computer on earth” é retórico e simplificador.
3. “Fastest way to actually understand a subject” é afirmação promocional, não analítica.
4. “5 foundational propositions” pode ser útil como heurística, mas não é uma regra universal.

### Erros conceptuais ou deslocações históricas

1. O texto aproxima Boole de uma lógica de falsificabilidade que é muito mais associada a Popper.
2. “Tudo se reduz a proposições verdadeiras ou falsas” é demasiado forte para domínios vagos, históricos, probabilísticos ou normativos.

### Omissões importantes

1. Não distingue proposições, definições e convenções.
2. Não trata limites de escopo.
3. Não trata conflito entre paradigmas.
4. Não trata incerteza, probabilidades e modelos parcialmente válidos.

---

## Versão Corrigida do Modelo Boole

Versão mais rigorosa:

> Ao entrar num domínio novo, identificar um pequeno conjunto de proposições estruturantes, hipóteses centrais ou restrições fundacionais. Para cada uma, explicitar evidência de suporte, condições de refutação, dependências com outras proposições, tensões internas e limites de validade. O objetivo não é reduzir o domínio a binários simplistas, mas tornar a sua estrutura explícita e auditável.

---

## Texto 2 — Zeigarnik

## Ideia Central

O texto apresenta um modelo de atenção e memória baseado em loops abertos:

- tarefas não encerradas mantêm ativação;
- tarefas concluídas tendem a ser libertadas;
- sistemas externos confiáveis reduzem tensão;
- plataformas podem explorar esse mecanismo.

No contexto deste projeto, isto é muito valioso porque o regime já opera sobre:

- claims pendentes;
- validações suspensas;
- bloqueios;
- estados não promovidos;
- artefactos provisórios.

---

## O que o texto oferece de útil

### 1. Modelo para claims em aberto

Nem todo o trabalho cognitivo termina em promoção. O projeto precisa de representar explicitamente:

- claims abertos;
- claims suspensos;
- claims bloqueados;
- claims fechados.

### 2. Justificação para materialização externa

O texto reforça uma intuição central do regime:

> o que fica apenas na cabeça mantém carga; o que entra num sistema confiável pode ser governado.

Isto articula-se bem com:

- `Documento Sombra`
- `Objeto Digital`
- `SystemUseRecord`
- filas de validação

### 3. Disciplina de fecho

O projeto pode usar este modelo para exigir que todo loop tenha um de poucos destinos válidos:

- `closed`
- `scheduled`
- `suspended`
- `blocked`
- `promoted`

---

## Erros, exageros e omissões no texto Zeigarnik

### Exageros

1. A narrativa do café é dramatizada.
2. “One of the most replicated findings in the history of psychology” é demasiado amplo.
3. “Most valuable insight in the history of media” é retórica forte, não análise cuidadosa.

### Fragilidades conceptuais

1. “Proved” é demasiado forte.
2. O texto trata extrapolações para Netflix, TikTok e notificações como se fossem demonstrações diretas.
3. A leitura de GTD está simplificada em excesso.

### Omissões importantes

1. Não distingue intensidade dos loops.
2. Não distingue loops triviais de loops com custo epistemológico alto.
3. Não discute quando um loop deve ser mantido aberto deliberadamente.
4. Não trata diferença entre resolução verdadeira e pseudo-fecho.

---

## Versão Corrigida do Modelo Zeigarnik

Versão mais rigorosa:

> Tarefas interrompidas, intenções não concluídas ou problemas sem fecho tendem a manter maior ativação cognitiva do que tarefas encerradas, sobretudo quando existe compromisso de retoma. Sistemas externos confiáveis podem reduzir esta carga ao materializar o compromisso, mas não equivalem sempre a resolução completa. Em ambientes digitais, esta dinâmica pode ser explorada para maximizar retenção atencional.

---

## Síntese dos Dois Modelos

### Boole

Responde a:

- quais são os fundamentos?
- o que depende de quê?
- o que é assunção e o que é conclusão?
- o que destruiria esta estrutura?

### Zeigarnik

Responde a:

- o que ficou aberto?
- o que está suspenso?
- o que continua a consumir atenção/governança?
- que tipo de fecho é necessário?

### Leitura conjunta

Boole fornece a **estrutura lógica**.

Zeigarnik fornece a **dinâmica da incompletude**.

O projeto precisa das duas.

---

## Integração no Projeto

## Camada 1 — Proposition Engine

Novo submodelo para materializar estrutura do domínio.

### Saídas esperadas

- `foundational_propositions`
- `assumptions`
- `derived_claims`
- `dependency_graph`
- `tension_map`
- `falsification_conditions`

### Integração com a state machine

- `F0`: definir intenção e domínio
- `F1`: extrair proposições fundacionais
- `F1.5`: classificar grounded/derived/hypothesis
- `F2`: mapear dependências e tensões
- `F4`: lint de refutabilidade e estrutura

---

## Camada 2 — Open Loop Engine

Novo submodelo para representar claims não resolvidos.

### Estados recomendados

- `OPEN`
- `SCHEDULED`
- `SUSPENDED`
- `BLOCKED`
- `CLOSED`
- `PROMOTED`

### Integração com o regime

- loops abertos vivem em `Documento Sombra`
- loops estabilizados podem virar `Objeto Digital`
- loops com síntese validada podem virar `Cápsula Conceptual`

---

## Integração com Componentes Existentes

### ACORDAR

Adicionar:

- intenção principal
- pergunta fundacional
- lista de loops iniciais

### LOADER/KERNEL

Adicionar autoridade explícita sobre:

- proposition extraction
- loop closure policy
- falsifiability lint

### GMIF

Usar GMIF não só como etiqueta, mas também como filtro:

- proposições fundacionais grounded com mais peso;
- hipóteses mantidas em loop aberto;
- claims derivados só promovíveis se cadeia de suporte estiver íntegra.

### BLOCK/PROMOTE

Bloquear quando:

- não há proposição fundacional suficiente;
- não há condição de falsificação minimamente definida;
- existem tensões fortes sem resolução;
- há loops críticos abertos sem compromisso confiável;
- há legitimacy insuficiente.

---

## Requisitos Novos Propostos

### RF-14: Proposition Extraction
- extrair proposições estruturantes de um domínio ou corpus

### RF-15: Dependency Mapping
- mapear assunções, conclusões e tensões

### RF-16: Falsifiability/Boundary Lint
- exigir condição de refutação ou limite operacional por proposição relevante

### RF-17: Open Loop Tracking
- manter registo de loops cognitivos abertos, suspensos e fechados

### RF-18: Trusted Closure
- permitir fecho por conclusão ou compromisso materializado confiável

### RF-19: Loop-Aware Promotion Gate
- impedir promoção quando existem loops críticos não resolvidos

---

## Conclusão

Estes dois textos não devem ser aceites literalmente.

Devem ser tratados como duas sementes arquiteturais:

- **Boole** para estruturação epistemológica;
- **Zeigarnik** para governação da incompletude.

Se forem integrados com rigor, o projeto deixa de ser apenas um sistema que classifica claims e passa a ser um sistema que:

- identifica fundamentos;
- mede tensões;
- controla loops;
- exige fecho materializado;
- e só promove o que foi explicitamente sustentado.
