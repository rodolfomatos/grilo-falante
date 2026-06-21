# Grilo Falante v3.0 - Manual Completo

**Versão:** 3.0.0
**Data:** 2026-04-15

---

## Índice Geral

### PARTE 1: Fundamentos
01. [O Que é o Grilo Falante?](PARTE_1_FUNDAMENTOS/01_o_que_e_o_grilo.md)
02. [Analogias Simples](PARTE_1_FUNDAMENTOS/02_analogias_simples.md)
03. [Instalação Rápida](PARTE_1_FUNDAMENTOS/03_instalacao.md)
04. [O Primeiro Ciclo](PARTE_1_FUNDAMENTOS/04_primeiro_ciclo.md)

### PARTE 2: Utilizador
05. [Regime Lifecycle](PARTE_2_UTILIZADOR/05_regime_lifecycle.md)
06. [Chat Governado](PARTE_2_UTILIZADOR/06_chat_gobernado.md)
07. [Fluxo Completo](PARTE_2_UTILIZADOR/07_fluxo_completo.md)
08. [Claims e GMIF](PARTE_2_UTILIZADOR/08_claims_gmif.md)
09. [Gaps e PINA](PARTE_2_UTILIZADOR/09_gaps_pina.md)
10. [Exemplos Práticos](PARTE_2_UTILIZADOR/10_exemplos_praticos.md)

### PARTE 3: Especialista
11. [Todas as MCP Tools](PARTE_3_ESPECIALISTA/11_todas_mcp_tools.md)
12. [Todos os REST Endpoints](PARTE_3_ESPECIALISTA/12_todos_rest_endpoints.md)
13. [Workflows](PARTE_3_ESPECIALISTA/13_workflows.md)
14. [Auditoria Hostil](PARTE_3_ESPECIALISTA/14_auditoria_hostil.md)

### PARTE 4: Administrador
15. [Arquitetura Técnica](PARTE_4_ADMINISTRADOR/15_arquitetura.md)
16. [Docker Setup](PARTE_4_ADMINISTRADOR/16_docker.md)
17. [Configuração](PARTE_4_ADMINISTRADOR/17_configuracao.md)
18. [Schema da Base de Dados](PARTE_4_ADMINISTRADOR/18_schema.md)

### PARTE 5: Profundidade
19. [Memória em Camadas](PARTE_5_PROFUNDIDADE/19_memoria_camadas.md)
20. [RAG e Pesquisa Semântica](PARTE_5_PROFUNDIDADE/20_rag_semantico.md)
21. [State Machine](PARTE_5_PROFUNDIDADE/21_estado_machine.md)
22. [Troubleshooting](PARTE_5_PROFUNDIDADE/22_troubleshooting.md)

### PARTE 6: Integrações
23. [MemPalace](PARTE_6_INTEGRACOES/23_mempalace.md)
24. [Graphify](PARTE_6_INTEGRACOES/24_graphify.md)
25. [OpenWebUI](PARTE_6_INTEGRACOES/25_openwebui.md)
26. [Ollama](PARTE_6_INTEGRACOES/26_ollama.md)
27. [AES](PARTE_6_INTEGRACOES/27_aes.md)

### PARTE 7: Referência
27. [Cheatsheet](PARTE_7_REFERENCIA/27_cheatsheet.md)
28. [Códigos de Erro](PARTE_7_REFERENCIA/28_codigos_erro.md)
29. [Glossário](PARTE_7_REFERENCIA/29_glossario.md)

### Apêndices
A1. [Código de Sessão e Resume](APENDICES/A1_session_resume.md)
A2. [Exemplos de Código](APENDICES/A2_exemplos_codigo.md)
A3. [FAQ](APENDICES/A3_faq.md)

---

## Navegação Rápida

| Para... | Ir para |
|---------|---------|
| O que é? | PARTE_1/01 |
| Instalar? | PARTE_1/03 |
| Usar /grilo chat? | PARTE_2/06 |
| Todas as tools? | PARTE_3/11 |
| Configurar Docker? | PARTE_4/16 |
| Resolver problemas? | PARTE_5/22 |
| Integrar Graphify? | PARTE_6/24 |
| Integrar AES? | PARTE_6/27 |
| Retomar sessão? | APENDICES/A1 |

---

## Como Ler Este Manual

### Níveis Feynman

Este manual está organizado em níveis de profundidade:

| Nível | Público | Estilo |
|-------|---------|--------|
| **PARTE 1** | Criança/Leigo | Analogias, imagens, passo-a-passo |
| **PARTE 2** | Utilizador | Fluxos completos, exemplos |
| **PARTE 3** | Especialista | Todas as tools, parâmetros |
| **PARTE 4** | Administrador | Docker, config, deployment |
| **PARTE 5** | Profundidade | Arquitetura interna, debugging |
| **PARTE 6** | Integradores | Graphify, MemPalace, OpenWebUI |

### Convenções

```bash
# Código bash
python3 grilo_pipeline.py <args>

# MCP tool
grilo_load()
grilo_acordar(temporal_anchor="...", intention="...")

# REST API
curl http://localhost:8001/api/v1/claims
```

---

## Quick Start

```bash
# 1. Instalar
docker-compose up -d

# 2. Iniciar chat governado
/grilo chat

# 3. Começar ciclo
> grilo_load()
> grilo_acordar(temporal_anchor="2026-04-15", intention="Analisar relatório")

# 4. Trabalhar
> A temperatura média global aumentou 1.1°C desde 1880.

# 5. Terminar
> :quit
```

---

## Sistema de Suporte

Para dúvidas:
1. Consulta o [FAQ](APENDICES/A3_faq.md)
2. Consulta o [Glossário](PARTE_7_REFERENCIA/29_glossario.md)
3. Abre uma issue em https://github.com/rodolfomatos/grilo-falante

---

*Este manual é parte do projeto Grilo Falante - Epistemic Governance Regime*
