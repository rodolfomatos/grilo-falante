# Skills Documentation

This directory contains documentation for the Grilo Falante skills system.

## Available Skills

### Shadow First

Metodologia de documentação que diz: antes de perguntar, pesquisar antes de assumir, analisar antes de implementar.

**Location:** `SHADOW_FIRST.md`

**Comandos:**
```bash
python -m grilo_admin.skills.cli check <concept>
python -m grilo_admin.skills.cli shadow <concept>
python -m grilo_admin.skills.cli ritual
python -m grilo_admin.skills.cli status
python -m grilo_admin.skills.cli report <theme>
```

---

## Adding New Skills

1. Create the skill module in `grilo_admin/skills/`
2. Add documentation in `docs/skills/`
3. Register in `grilo_admin/skills/__init__.py`
4. Update this README

---

## Structure

```
docs/skills/
├── README.md        # This file
├── SHADOW_FIRST.md  # Shadow First methodology
└── ...

grilo_admin/skills/
├── __init__.py
├── shadow_first.py  # Shadow First implementation
├── registry.py      # Concept registry
└── cli.py          # CLI interface
```
