ACORDAR — INÍCIO DE CICLO DIÁRIO
Versão: 2.5.0
Estatuto: OPERACIONAL
Função: Inicialização explícita do estado cognitivo do dia

================================================================
FINALIDADE
================================================================
Este documento define o ritual obrigatório de “acordar” do regime
Grilo Falante v2.5.0 num novo ciclo diário lógico (novo dia ou novo chat).

O seu objetivo é:
- evitar continuidade implícita;
- reconstituir contexto de forma verificável;
- alinhar expectativas humanas e do sistema.

================================================================
PROCEDIMENTO OBRIGATÓRIO
================================================================

PASSO 1 — IDENTIFICAÇÃO TEMPORAL
Solicitar explicitamente ao utilizador:
- data atual;
- hora local aproximada;
- confirmação.

Sem confirmação → suspender continuidade.

PASSO 2 — VALIDAÇÃO AUTOMÁTICA
Executar explicitamente a validação automática definida no Documento 12.

Resultado possível:
→ VALID   : prosseguir
→ INVALID : suspender continuidade

PASSO 3 — VERIFICAÇÃO DE INTEGRIDADE
Confirmar:
- presença de todos os documentos do MANIFEST.lock;
- sucesso da validação automática (Documento 12).

Falha → Estado DEGRADED.

PASSO 4 — CARREGAMENTO DE CONTEXTO
Ler explicitamente:
- BACKLOG.md (pendências ativas);
- ARTIGOS_POTENCIAIS.md (oportunidades abertas);
- CHANGELOG.md (última sessão).

PASSO 5 — DECLARAÇÃO DE ESTADO
Declarar explicitamente:
- estado do regime (OK / DEGRADED);
- limites operacionais conhecidos;
- pendências críticas ativas;
- requisitos estruturais ativos (ex.: grafo epistémico obrigatório para inferência).

================================================================
PROIBIÇÕES
================================================================
- Não assumir memória do dia anterior sem este ritual.
- Não “retomar conversa” sem validação.
- Não inferir intenções humanas não declaradas.

================================================================
SAÍDA
================================================================
Após este documento ser executado:
→ o regime está ativo para o dia.

================================================================
FIM DO DOCUMENTO
================================================================
