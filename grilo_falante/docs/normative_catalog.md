# NORMATIVE CATALOGUE (NC)

## Version
v2.5.0

## Status
Canonical • Operational

---

# 0. Function of this document

The **Normative Catalogue (NC)** is the artefact responsible for recording all **Normative Occurrences (NO)** detected during a reasoning cycle.

The catalogue provides **traceability without activation**.

Its role is to:

- preserve detected normative material;
- prevent implicit promotion of textual norms;
- enable later review and candidate selection;
- support the PINA protocol.

The catalogue **does not activate rules**.

---

# 1. Position in the Epistemic Pipeline

The Normative Catalogue operates between **norm detection** and **norm incorporation**.

Pipeline:

Text
↓
Normative Occurrence (NO)
↓
Normative Catalogue (NC)
↓
Normative Candidate (NCA)
↓
PINA Gate
↓
Active Invariant

The catalogue therefore functions as a **buffer layer** between observation and governance.

---

# 2. Catalogue Entry Structure

Each catalogue entry MUST contain the following fields.

## Required Fields

NO-ID
Unique identifier for the occurrence.

Source
Document or artefact where the rule appears.

Quote
Faithful textual quote of the normative statement.

Location
Section, page, or line reference.

Type
Norm category:

- Methodological rule
- Prohibition
- Constraint
- Legitimacy condition
- Interpretative restriction

---

# 3. Example Entry

NO-04

Source: DOCUMENTO_05_Fundamento_Cognitivo.md

Quote:
"Structure does not imply inference."

Location:
Section "Modelo Cognitivo"

Type:
Methodological rule

Status:
Recorded (not active)

---

# 4. Catalogue Status

Entries in the catalogue have one of the following states.

RECORDED
The occurrence has been detected but not proposed as a candidate.

CANDIDATE
The occurrence has been proposed for incorporation and triggers PINA.

RESOLVED
The rule has been processed by PINA.

States are updated during the reasoning cycle.

---

# 5. Catalogue Governance

The assistant MUST:

1. record all detected normative occurrences;
2. avoid activating them implicitly;
3. preserve faithful textual representation;
4. allow later transformation into Normative Candidates.

The assistant MUST NOT:

- treat catalogue entries as operative rules;
- derive constraints from them;
- assume incorporation.

---

# 6. Relation to PINA

The catalogue is the **input layer** of the PINA protocol.

Only entries promoted to **Normative Candidate (NCA)** status may trigger the PINA decision gate.

Catalogue entries remain inert until explicitly proposed for incorporation.

---

# 7. Persistence

The catalogue SHOULD be materialised as a persistent artefact for the cycle.

Possible implementations:

- normative_catalog.md
- ledger entry
- structured table

Persistence ensures auditability of normative detection.

---

# 8. Integrity Rule

Failure to record detected normative occurrences constitutes a **loss of epistemic traceability**.

The catalogue therefore functions as a **memory layer for normative detection** without activating rules.

---

# End of Document

