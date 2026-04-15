# Guia de Criação de Repositório Público
## Grilo Falante UNI

## Objetivo do Repositório

O repositório público do **Grilo Falante UNI** deve cumprir três funções simultâneas:

1. **Arquivo canónico** — preservar versões fechadas, auditáveis e citáveis do regime.
2. **Transparência epistémica** — permitir avaliação independente por terceiros, sem dependência de autoridade implícita.
3. **Porta de entrada UX** — facilitar compreensão, instalação e orientação inicial para novos utilizadores.

Este não é um repositório de código. É um repositório de **regime normativo**.

---

## Estrutura Recomendada do Repositório

```
grilo-falante-uni/
├── README.md
├── LICENSE
├── releases/
│   └── v1.6.4/
│       ├── installer/
│       │   └── grilo_falante_uni_v1.6.4.md
│       │
│       ├── integrity/
│       │   └── grilo_falante_uni_v1.6.4.sha256
│       │
│       ├── ledger/
│       │   └── Documento_06_Ledger_v1.6.4.md
│       │
│       └── README_RELEASE.md
│
├── docs/
│   ├── philosophy.md
│   └── faq.md
│
└── CHANGELOG.md
```

---

## README.md (Raiz do Repositório)

O README da raiz não governa o regime. Serve como **documento de orientação externa**.

Conteúdo mínimo recomendado:

- O que é o Grilo Falante UNI;
- Para que serve e para que não serve;
- Como instalar (copy–paste do Installer);
- Onde se encontra a versão atual;
- Princípios-chave (fluência ≠ validade, responsabilidade humana, etc.);
- Licença;
- Autoria.

Evitar reproduzir documentos canónicos neste ficheiro.

---

## Pasta `releases/`

A pasta `releases` contém exclusivamente versões fechadas e auditáveis do regime.

### Installer

```
releases/v1.6.4/installer/grilo_falante_uni_v1.6.4.md
```

Este ficheiro:
- é o **Documento 00**;
- é o texto que o utilizador copia para instalar;
- é a fonte normativa única;
- não deve ser alterado após publicação.

### Integrity

```
releases/v1.6.4/integrity/grilo_falante_uni_v1.6.4.sha256
```

Contém a hash SHA-256 do Installer correspondente.

Serve como selo técnico de integridade e base para auditoria.

### Ledger

```
releases/v1.6.4/ledger/Documento_06_Ledger_v1.6.4.md
```

Regista a evolução histórica do regime, incluindo:
- versão;
- natureza da alteração;
- hash;
- método e ambiente de cálculo;
- estado de canonicidade.

### README_RELEASE.md

Documento técnico curto que descreve:
- o que é a release;
- o que mudou face à versão anterior;
- se existem novas invariantes;
- como verificar integridade;
- como instalar.

---

## Pasta `docs/`

Contém apenas material explicativo e não normativo.

Exemplos:
- `philosophy.md` — fundamentos conceptuais e racionais;
- `faq.md` — esclarecimento de dúvidas frequentes.

Nada nesta pasta tem autoridade normativa.

---

## LICENSE

O ficheiro LICENSE deve conter:

**Creative Commons Attribution–ShareAlike 4.0 International (CC BY-SA 4.0)**

Sem variações nem ambiguidades.

---

## CHANGELOG.md

Documento factual e sucinto, alinhado com o Ledger.

Exemplo:

```
## v1.6.4
- Consolidação exportável final
- Introdução formal de fingerprint
- Grafo canónico do installer
- Nenhuma nova invariante epistémica
```

---

## Boas Práticas

- Publicar apenas versões fechadas;
- Nunca editar um Installer após release;
- Separar claramente norma de explicação;
- Garantir que o Installer é sempre autocontido.

---

## Conclusão

Esta estrutura permite que o Grilo Falante UNI seja arquivado, auditado, citado e reutilizado de forma robusta, sem dependência de plataformas específicas ou autoridade implícita.

