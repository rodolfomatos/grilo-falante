---
project: Grilo Falante v3.0
created: 2026-06-08
current_sprint: sprint-01
current_ticket: ""
last_updated: 2026-06-08
---

# Grilo Falante v3.0 Project Kanban

## Project Overview
Grilo Falante v3.0 is an epistemic governance regime that helps make the cost of judgment visible without producing decisions or validating truths.

## Current State
- **Current Sprint:** sprint-01
- **Current Ticket:** None (ready for planning)

## Swimlanes
- **Backlog** → Items awaiting prioritization
- **In Progress** → Items actively being worked on
- **Review** → Items completed but awaiting review
- **Done** → Items completed and reviewed

## Workflow
1. Plan phase (/aes-plan) → creates aes/tickets/TXXX-plan.md
2. Build phase (/aes-build) → creates aes/tickets/TXXX-build.md with diffstory
3. Verify phase (/aes-verify) → runs quality gates, creates aes/tickets/TXXX-verify.md
4. Review phase (/aes-review) → code review, creates aes/tickets/TXXX-review.md
5. Learn phase (/aes-learn) → documents lessons, creates aes/tickets/TXXX-learn.md

## How to Use
- To start work on a ticket: `/aes-plan` followed by `/aes-build`, `/aes-verify`, `/aes-review`, `/aes-learn`
- To run full cycle: `/aes run TXXX` (with confirmation between phases)
- To work on all tickets in sprint: `/aes sprint`
- For automatic execution: `/aes auto` (stops on failures)

## Notes
- This file is the single source of truth for project state
- Update current_sprint and current_ticket as work progresses
- All tickets should follow the AES execution loop
- Hostile analysis is required before implementation