# Quality Checklists

## Pre-commit (quick)

Estas verificações devem ser feitas antes de fazer commit de qualquer alteração:

- [ ] **Tests pass**: `PYTHONPATH=. make test` ou equivalente
- [ ] **Lint passes**: `PYTHONPATH=. make lint` (ruff check)
- [ ] **Format correct**: `PYTHONPATH=. make format` (ruff format - verifica se não há alterações necessárias)
- [ ] **No console.log/debug in src**: Verificar que não há statements de debug no código
- [ ] **No TODO in src**: Verificar que não há comentários TODO no código fonte
- [ ] **Docs updated**: Se o comportamento mudou, a documentação foi atualizada
- [ ] **Diffstory written**: No output da fase de build, explicar o que mudou, por quê, o que foi intencionalmente deixado intacto, e riscos restantes

## Pre-release (thorough)

Estas verificações devem ser feitas antes de um release:

### General
- [ ] Todos os checks de pré-commit acima
- [ ] Documentação de API atualizada (se aplicável)
- [ ] Changelog atualizado
- [ ] Version bumped adequadamente
- [ ] Build artifacts limpos e reconstruídos

### Backend-specific (Python/FastAPI)
- [ ] Nenhuma dependência desnecessária ou não utilizada
- [ ] Todas as variáveis de ambiente usadas têm defaults ou são documentadas
- [ ] Tratamento adequado de erros em todos os endpoints
- [ ] Validação de entrada em todos os endpoints
- [ ] Rate limiting implementado onde apropriado
- [ ] CORS configurado corretamente
- [ ] Headers de segurança apropriados (X-Frame-Options, etc.)

### Frontend-specific (if applicable)
- [ ] Nenhum erro no console do browser
- [ ] Design responsivo verificado em múltiplos tamanhos de tela
- [ ] Acessibilidade básica verificada (contraste, navegação por teclado)
- [ ] Nenhum uso de bibliotecas com vulnerabilidades conhecidas

### Security
- [ ] Nenhuma senha ou chave hardcoded no código
- [ ] Injeções SQL/NoSQL prevenidas
- [ ] XSS prevenido em saídas HTML
- [ ] CSRF protection onde aplicável
- [ ] Dependências verificadas para vulnerabilidades conhecidas

### Performance
- [ ] Nenhum vazamento de memória óbvio
- [ ] Consultas de banco de dados otimizadas (se aplicável)
- [ ] Uso adequado de caching
- [ ] Timeouts configurados para chamadas externas

### Testing
- [ ] Cobertura de testes adequada (meta do projeto: 80%+)
- [ ] Testes de unidade passando
- [ ] Testes de integração passando (se aplicável)
- [ ] Testes de ponta-a-ponta passando (se aplicável)
- [ ] Testes cobrem casos de uso típicos e edge cases

### Documentation
- [ ] README atualizado com instruções de instalação e uso
- [ ] Todos os parâmetros de função/documentados
- [ ] Exemplos de uso claros e funcionais
- [ ] Arquitetura e fluxos de dados documentados
- [ ] Decisões de design importantes explicadas

## Domain Specific Quality Gates (from docs/QUALITY_GATES.md)

Para verificar qualidade específica do domínio, consulte `docs/QUALITY_GATES.md` e aplique os portões relevantes:

### Epistemic Governance Specific
- [ ] Regime não produz decisões ou valida verdades (apenas torna visível o custo)
- [ ] Toda saída tem rasto verificável para afirmações epistemicas
- [ ] Estados de legitimidade funcionam corretamente (SUSPENDED por padrão)
- [ ] Protocolo Shadow First seguido (pesquisa antes de assumir)
- [ ] Classificações GMIF são consistentes e bem fundamentadas
- [ ] Transições entre estados de claim são validadas adequadamente
- [ ] Feedback humano é requerido para afirmações de legitimidade
- [ ] Grafos de conhecimento são materializados e referenciados explicitamente

## How to Use

1. Para trabalho diário, use a lista de pré-commit antes de cada commit
2. Antes de um release ou deploy, execute a lista completa de pré-release
3. Se algum item falhar, corrija antes de prosseguir
4. Atualize estas listas conforme a equipe aprende e o projeto evolui
5. Considere automatizar estas verificações com git hooks ou CI/CD quando apropriado