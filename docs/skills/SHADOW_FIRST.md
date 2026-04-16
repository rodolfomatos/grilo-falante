# SKILLS — Shadow First Methodology

**Versão:** 2.0
**Data:** 2026-04-16
**Origem:** Sessão de correção conceptual do modelo PEDRA

---

## 1. O que é o Shadow First?

**Shadow First** é uma metodologia de trabalho que diz:

> Antes de perguntar, assumption, ou implementar, deves primeiro pesquisar documentação, criar Shadow Document do que encontraste, e gerar FAQ com perguntas que ainda tens.

### A Lição Central

> "Se me estás a perguntar isso, é porque não fizeste um documento sombra!"

---

## 2. Quando Invocar

### 2.1 Situações Automáticas

Invoca o skill `/shadow_first` quando:
- O utilizador menciona algo que "já falámos várias vezes"
- Não sabes algo que o utilizador pensa que já devias saber
- Começas a perguntar "o que é X?" sem teres pesquisado
- O utilizador corrige algo que devias ter investigado

### 2.2 Ritual Pré-Sessão

```
/shadow_first ritual
```

Verifica **Shadow Debt** antes de começar trabalho.

---

## 3. Conceitos Fundamentais

### 3.1 Shadow Debt (Dívida de Sombra)

Conceitos mencionados pelo utilizador mas ainda não documentados.

```
SHADOW DEBT (4 conceitos)
├── MemPalace          ← mencionado em 3 sessões
├── PEDRA              ← corrigido após confusão
├── ConceptualCapsule   ← mencionado mas não shadowed
└── DigitalObject      ← mesmo
```

### 3.2 Shadow Score (Pontuação)

Métrica de documentação:

| Score | Significado |
|-------|-------------|
| 100% | Conceito completamente documentado |
| 50% | Tem shadow doc, mas falta FAQ ou relatório |
| 0% | Mencionado mas nunca documentado |

### 3.3 Concept Registry (Registo de Conceitos)

Índice central de todos os conceitos documentados:

```
docs/shadow_documents/REGISTRY.md
```

---

## 4. Comandos

### 4.1 CLI

```bash
# Verificar se conceito está documentado
python -m grilo_admin.skills.cli check <concept>

# Iniciar sessão de documentação
python -m grilo_admin.skills.cli shadow <concept>

# Verificar shadow debt
python -m grilo_admin.skills.cli ritual

# Ver estado geral
python -m grilo_admin.skills.cli status

# Gerar relatório de sessão
python -m grilo_admin.skills.cli report <theme> --concepts=c1,c2
```

### 4.2 API Endpoints

```
GET  /admin/skills/shadow/check/<concept>
POST /admin/skills/shadow/session
GET  /admin/skills/shadow/session/<concept>
POST /admin/skills/shadow/session/<concept>/content
POST /admin/skills/shadow/session/<concept>/faq
POST /admin/skills/shadow/session/<concept>/complete
GET  /admin/skills/shadow/ritual
GET  /admin/skills/shadow/status
POST /admin/skills/shadow/report
```

---

## 5. Workflow Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    SHADOW FIRST WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. MENCÃO                                                │
│     Utilizador menciona conceito                            │
│           ↓                                                  │
│  2. CHECK                                                  │
│     /shadow_first check <conceito>                        │
│           ↓                                                  │
│  ┌─────────────────────────────────────────┐                │
│  │ ESTÁ DOCUMENTADO?                      │                │
│  └─────────────────────────────────────────┘                │
│         ↓ SIM                    ↓ NÃO                      │
│  ✅ Usar documentação      ⚠️ SHADOW DEBT                  │
│     existente                 ↓                             │
│                          3. SHADOW                        │
│                          /shadow_first shadow <conceito>  │
│                                 ↓                          │
│                          4. PESQUISAR                     │
│                          webfetch / grep / glob           │
│                                 ↓                          │
│                          5. DOCUMENTAR                    │
│                          - SHADOW_<CONCEITO>_v1.md       │
│                          - FAQ_<CONCEITO>_GF.md           │
│                          - REGISTRY.md                    │
│                                 ↓                          │
│                          6. PERGUNTAR                     │
│                          Só agora, o que não soube        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Estrutura de Documentos

### 6.1 Shadow Document

```
docs/shadow_documents/SHADOW_<CONCEITO>_v1.md
```

- **Não é canónico** - é análise, não definição
- Guarda claims, não conclusions
- Identifica gaps, não resolve tudo

### 6.2 FAQ

```
docs/shadow_documents/FAQ_<CONCEITO>_GF_v1.md
```

- Perguntas genuínas, não retóricas
- Identifica o que ainda não sabes
- Prepara perguntas para o utilizador

### 6.3 Relatório de Sessão

```
docs/reports/RELATORIO_SESSAO_<TEMA>_YYYYMMDD.md
```

- Para reentrada futura
- Estado atual do trabalho
- Próximos passos claros
- Lições aprendidas

---

## 7. Regras de Ouro

1. **Nunca perguntes o que podes pesquisar**
2. **Nunca assumas o que não documentaste**
3. **Shadow debt não perdoa - cria o doc**
4. **FAQ não é para ti - é para saberes o que perguntar**
5. **Relatório é para o teu EU futuro - documenta como se fosses outro**
6. **Documenta tudo sempre - para tu próprio não te perderes**
7. **Memória é contextual - o mesmo conceito pode ter significados diferentes**

---

## 8. Integração com Outros Skills

### 8.1 Com grilo_falante

```
/grilo_falante
→ Analisa conceito no contexto do GF
→ Verifica se já existe em docs/
```

### 8.2 Com gepeto

```
/gepeto
→ Identifica knowledge gaps
→ Se gap é sobre conceito externo, invoke shadow_first
```

### 8.3 Com graphify

```
/graphify
→ Transforma shadow docs em knowledge graph
→ Mostra conexões entre conceitos
```

---

## 9. Código

### 9.1 Módulo Principal

```python
from grilo_admin.skills import ShadowFirstSkill, ConceptRegistry

# Verificar conceito
skill = ShadowFirstSkill()
result = skill.check("MemPalace")

# Iniciar sessão
session = skill.shadow("MemPalace")

# Adicionar conteúdo
skill.add_shadow_content("MemPalace", "# Shadow content...", sources=["github.com/MemPalace"])

# Adicionar FAQ
skill.add_faq("MemPalace", "Como funciona o retrieval?", answer="...")

# Completar sessão
skill.complete_session("MemPalace")

# Ritual pré-sessão
ritual = skill.ritual()

# Status
status = skill.status()
```

### 9.2 Registry

```python
registry = ConceptRegistry()
registry.register_concept("MemPalace", mentioned_by="Rodolfo")
registry.update_concept("MemPalace", shadow_doc_path="docs/shadow_documents/SHADOW_MEMPALACE_v1.md")
score = registry.get_shadow_score()
debt = registry.get_shadow_debt()
```

---

## 10. Ficheiros

### 10.1 Código

```
grilo_admin/skills/
├── __init__.py
├── shadow_first.py   # ShadowFirstSkill class
├── registry.py      # ConceptRegistry class
└── cli.py          # CLI interface
```

### 10.2 Documentação

```
docs/skills/
├── SHADOW_FIRST.md  # Este documento
└── ...

docs/shadow_documents/
├── REGISTRY.md      # Índice central
├── SHADOW_*.md      # Shadow documents
└── FAQ_*.md         # FAQs
```

### 10.3 Scripts

```
scripts/
├── create_shadow_first_ilha.py
└── verify_shadow_first_ilha.py
```

---

## 11. Estado Atual

| Componente | Estado |
|------------|--------|
| Módulo Código | ✅ Implementado |
| CLI | ✅ Implementado |
| API Endpoints | ⏳ A implementar |
| ILHA em memória | ✅ Implementado |
| Persistência | ⏳ A implementar |
| Documentação | ✅ Este documento |

---

## 12. Próximos Passos

1. [ ] Implementar API endpoints para skills
2. [ ] Adicionar persistência (ILHAManager ou PostgreSQL)
3. [ ] Criar ILHA "Shadow First" permanente
4. [ ] Integrar com MemPalace
5. [ ] Testar workflow completo

---

**FIM DO DOCUMENTO**
