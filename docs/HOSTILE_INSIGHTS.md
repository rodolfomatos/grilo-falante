# Hostile Insights Registry

Registo de lições aprendidas através de análise hostil durante o desenvolvimento do Grilo Falante v3.0.

---

## [AES Compliance] - Sprint-01 marcado como "done" sem evidência nos tickets
- **Task**: AES Alignment (commit 45f7d63)
- **Insight**: O sprint-01 lista 7 tickets (T001-T007) como "done", mas `aes/tickets/` está vazio. Não há ficheiros TXXX-*.md. Isto significa que o sprint foi marcado como completo sem que as fases de plan/build/verify/review/learn fossem executadas.
- **Origin**: Verificação direta do diretório aes/tickets/
- **Impact**: Perda de rastreabilidade. Um novo agente não consegue saber o que foi realmente feito.
- **Applied To**: Sprint-02 deve garantir que tickets têm evidência real antes de fechar.
- **Date**: 2026-06-20

---

## [AES Compliance] - HOSTILE_INSIGHTS.md não existia
- **Task**: Análise do projeto (sessão atual)
- **Insight**: Ficheiro listado como "Critical File" no CLAUDE.md, mas não foi criado durante a integração AES. Nenhum registro de lições hostis existia no projeto.
- **Origin**: ls docs/HOSTILE_INSIGHTS.md → MISSING
- **Impact**: Conhecimento gerado por análises hostis é perdido entre sessões.
- **Applied To**: Criado nesta sessão. Todos os contribuidores devem atualizá-lo.
- **Date**: 2026-06-20

---

## [Makefile Anti-Pattern] - 2>/dev/null esconde falhas silenciosamente
- **Task**: Análise do projeto (sessão atual)
- **Insight**: Os targets `test`, `lint`, `format` usam `2>/dev/null` para engolir erros. Isto significa que se o ruff ou pytest não estiverem instalados, o make reporta sucesso. Em CI, isto causaria falsos positivos. AES deve detetar este padrão como um quality smell.
- **Origin**: Leitura do Makefile, linhas 95-108 e 111-126
- **Impact**: Falsos positivos em CI. Debugging difícil.
- **Applied To**: Removido nesta sessão. Substituído por verificações explícitas de dependências.
- **Date**: 2026-06-20

---

## [Documentação Duplicada] - docs/reference/ vs docs/references/
- **Task**: Reconhecimento do projeto
- **Insight**: Existem dois diretórios com documentação sobreposta: `docs/reference/` (17 ficheiros) e `docs/references/` (5 ficheiros). Pelo menos 3 ficheiros são duplicados. Isto causa confusão sobre qual é a fonte de verdade.
- **Origin**: Exploração de diretórios, leitura de ambos os índices
- **Impact**: Informação contraditória, manutenção duplicada.
- **Applied To**: docs/references/ marcado como obsoleto. Criado README a redirecionar para docs/reference/.
- **Date**: 2026-06-20

---

## [Pydantic Deprecation] - Config class-based em vez de ConfigDict
- **Task**: Execução de testes
- **Insight**: 11 warnings de deprecação do Pydantic V2: `Support for class-based config is deprecated, use ConfigDict instead`. Adicionalmente, campos `model_name` e `model_used` conflitam com o namespace protegido `model_`.
- **Origin**: pytest warnings durante test_models.py e test_services.py
- **Impact**: Código vai quebrar no Pydantic V3. Já existem avisos em cada execução.
- **Applied To**: Adicionado ao backlog do sprint-02.
- **Date**: 2026-06-20

---

## [Dívida Técnica] - Lint tem ~100+ problemas pré-existentes
- **Task**: Verificação de qualidade
- **Insight**: `ruff check` revela dezenas de problemas: imports não ordenados, typing deprecated (Dict/List em vez de dict/list), imports não utilizados, variável ambígua `l`, ficheiro com nome inválido `erosão.py` (N999), linhas demasiado longas.
- **Origin**: Execução de ruff check na sessão atual
- **Impact**: Dificulta revisão de código, reduz confiança na base de código.
- **Applied To**: Adicionado ao backlog do sprint-02. Não corrigido nesta sessão por ser scope creep.
- **Date**: 2026-06-20

---

## [AES Protocol Gap] - Faltam verificações de evidência entre fases
- **Task**: Análise do protocolo AES
- **Insight**: O AES define que cada fase produz ficheiros, mas não verifica se esses ficheiros realmente existem antes de avançar. O sprint-01 prova que é possível marcar tickets como "done" sem criar os artefactos. O protocolo I/O Contract diz que deve verificar `requires`, mas isto não foi aplicado.
- **Origin**: Observação do gap entre sprint-01 claim e realidade
- **Impact**: Perda de rastreabilidade, especialmente em sessões multi-agente.
- **Applied To**: Sugestão para AES: adicionar verificação explícita de artefactos antes de permitir transição de fase.
- **Date**: 2026-06-20
