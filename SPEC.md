# Grilo Falante Chat - Technical Specification

## Overview

The Grilo Falante Chat is an integrated conversation interface where the chat module is a core part of the epistemic governance system, not a separate addon. The metaphor is:
- **Chat** = ears (input)
- **LLM** = capacity to interpret speech
- **Grilo Falante** = memory and truth verification

All are part of the same "brain".

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Browser)                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ NAVBAR: Grilo Falante | Chat | Hub | Visualizer | Sources  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                   CHAT INTERFACE (/chat)                     │   │
│  │  ┌─────────┐  ┌─────────────────────────────────────────┐  │   │
│  │  │CONVERSA-│  │  Bubbles: user/assistant                 │  │   │
│  │  │TIONS    │  │  with epistemic indicators               │  │   │
│  │  │         │  │                                         │  │   │
│  │  │ Today   │  │  ⚠️ Claims: 2 new  ❓ Gaps: 1           │  │   │
│  │  │ ├ Ses 1 │  │                                         │  │   │
│  │  │ └ Ses 2 │  └─────────────────────────────────────────┘  │   │
│  │  │         │  ┌─────────────────────────────────────────┐  │   │
│  │  │Yesterday│  │ [Input] [Send]                          │  │   │
│  │  └─────────┘  └─────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GRILO FALANTE API (FastAPI)                     │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    CHAT ENDPOINTS                              │ │
│  │  GET  /api/v1/chat/conversations     → list all               │ │
│  │  POST /api/v1/chat/conversations     → create new             │ │
│  │  GET  /api/v1/chat/conversations/{id} → get conversation      │ │
│  │  DELETE /api/v1/chat/conversations/{id} → delete (GDPR)       │ │
│  │  POST /api/v1/chat/message          → send message (streaming)│ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                     │
│  ┌────────────────────────────┼────────────────────────────────┐ │
│  │           MESSAGE PROCESSING PIPELINE                          │ │
│  │                                                              │ │
│  │  1. message → intent_classification                           │ │
│  │  2. message → extract_claims (if factual)                     │ │
│  │  3. message → identify_gaps                                   │ │
│  │  4. retrieve_context (RAG from conversation + claims)          │ │
│  │  5. generate_response (LLM + context, streaming)              │ │
│  │  6. store_messages                                           │ │
│  │  7. async: iterative_re_eval (background task)               │ │
│  │  8. async: update_knowledge_graph                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                     │
│  ┌────────────────────────────┼────────────────────────────────┐ │
│  │                    EXISTING MODULES                           │ │
│  │  • Claims (already exists)                                    │ │
│  │  • Gaps (already exists)                                      │ │
│  │  • Knowledge Graph (already exists)                           │ │
│  │  • Sources (already exists)                                   │ │
│  │  • LLM Providers (Ollama, IAEDU, etc.)                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL     │
                    │   + pgvector    │
                    │                  │
                    │  • messages      │
                    │  • conversations│
                    │  • claims       │
                    │  • gaps         │
                    │  • sources      │
                    └─────────────────┘
```

---

## Database Schema

### New Tables

```sql
-- Conversations (threads)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    user_id TEXT NOT NULL DEFAULT 'anonymous',

    -- Metadata
    model_used TEXT,
    message_count INTEGER NOT NULL DEFAULT 0,

    -- Status
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_message_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS conversations_key_idx ON conversations(conversation_key);
CREATE INDEX IF NOT EXISTS conversations_user_idx ON conversations(user_id);
CREATE INDEX IF NOT EXISTS conversations_updated_idx ON conversations(updated_at DESC);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_key TEXT UNIQUE NOT NULL,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Content
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,

    -- LLM Metadata
    model TEXT,
    tokens_used INTEGER,
    inference_time_ms INTEGER,

    -- Epistemic state
    claims_detected JSONB DEFAULT '[]',
    gaps_identified JSONB DEFAULT '[]',
    gmif_level TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS messages_conversation_idx ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS messages_created_idx ON messages(created_at DESC);

-- Message-Claim links (N:M)
CREATE TABLE IF NOT EXISTS message_claims (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    claim_id INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL DEFAULT 'mentions', -- 'mentions', 'creates', 'resolves'
    salience REAL NOT NULL DEFAULT 0.5,
    UNIQUE(message_id, claim_id)
);

CREATE INDEX IF NOT EXISTS message_claims_message_idx ON message_claims(message_id);
CREATE INDEX IF NOT EXISTS message_claims_claim_idx ON message_claims(claim_id);

-- Message-Gap links (N:M)
CREATE TABLE IF NOT EXISTS message_gaps (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    gap_id INTEGER NOT NULL REFERENCES gaps(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL DEFAULT 'identifies', -- 'identifies', 'resolves'
    UNIQUE(message_id, gap_id)
);

CREATE INDEX IF NOT EXISTS message_gaps_message_idx ON message_gaps(message_id);
CREATE INDEX IF NOT EXISTS message_gaps_gap_idx ON message_gaps(gap_id);
```

---

## Data Models

### Conversation
```python
class Conversation(BaseModel):
    id: Optional[int]
    conversation_key: str
    title: str = "New Conversation"
    user_id: str = "anonymous"
    model_used: Optional[str] = None
    message_count: int = 0
    is_archived: bool = False
    created_at: datetime
    updated_at: Optional[datetime]
    last_message_at: Optional[datetime]
```

### Message
```python
class Message(BaseModel):
    id: Optional[int]
    message_key: str
    conversation_id: int
    role: str  # 'user' or 'assistant'
    content: str
    model: Optional[str]
    tokens_used: Optional[int]
    inference_time_ms: Optional[int]
    claims_detected: list[int] = []  # claim IDs
    gaps_identified: list[int] = []  # gap IDs
    gmif_level: Optional[str]
    created_at: datetime
```

### ChatRequest
```python
class ChatRequest(BaseModel):
    conversation_key: str
    message: str
    stream: bool = True
```

### ChatResponse (streaming)
```python
class ChatResponse(BaseModel):
    message_key: str
    conversation_key: str
    content: str
    claims: list[ClaimSummary]
    gaps: list[GapSummary]
    model: str
    done: bool
```

---

## API Endpoints

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chat/conversations` | List all conversations |
| POST | `/api/v1/chat/conversations` | Create new conversation |
| GET | `/api/v1/chat/conversations/{key}` | Get conversation with messages |
| PATCH | `/api/v1/chat/conversations/{key}` | Update conversation (title, archive) |
| DELETE | `/api/v1/chat/conversations/{key}` | Delete conversation (GDPR) |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/message` | Send message (streaming SSE) |
| GET | `/api/v1/chat/messages/{conversation_key}` | Get messages for conversation |

### Epistemic

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chat/conversations/{key}/claims` | Get all claims from conversation |
| GET | `/api/v1/chat/conversations/{key}/gaps` | Get all gaps from conversation |
| POST | `/api/v1/chat/conversations/{key}/reevaluate` | Trigger re-evaluation |

---

## Message Processing Pipeline

```
USER MESSAGE
     │
     ▼
┌────────────────────────────┐
│ 1. INTENT CLASSIFICATION  │
│    Classify as:           │
│    - question             │
│    - statement           │
│    - command              │
│    - creative             │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 2. CLAIM EXTRACTION        │
│    If statement/factual:   │
│    → extract claims        │
│    → create in DB          │
│    → link to message       │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 3. GAP IDENTIFICATION      │
│    → identify knowledge    │
│      gaps                  │
│    → create gaps in DB     │
│    → link to message       │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 4. RAG CONTEXT RETRIEVAL   │
│    - conversation history  │
│    - relevant claims (65%) │
│    - relevant gaps (35%)   │
│    - sources              │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 5. LLM RESPONSE (streaming)│
│    - context + prompt     │
│    - stream to client     │
│    - collect response     │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 6. STORE MESSAGES          │
│    - user message         │
│    - assistant message    │
│    - link claims/gaps     │
└────────────────────────────┘
     │
     ▼ (async)
┌────────────────────────────┐
│ 7. BACKGROUND TASKS       │
│    a) Re-evaluate previous │
│       claims in thread     │
│    b) Update knowledge    │
│       graph               │
│    c) Trigger school mode │
│       if gaps > threshold │
└────────────────────────────┘
```

---

## Streaming Response Format (SSE)

```text
event: claim
data: {"id": 123, "claim_text": "The Roman Empire fell in 476 AD", "gmif_level": "M2"}

event: gap
data: {"id": 45, "reason": "What caused the Western Roman Empire to fall?"}

event: chunk
data: {"content": "The Roman Empire "}

event: chunk
data: {"content": "was a "}

event: done
data: {"message_key": "abc123", "tokens": 150, "time_ms": 2300}
```

---

## Frontend Structure

### Files
```
chat/
├── index.html          # Main chat page
├── chat.js             # Client-side logic
├── chat.css            # Styles
└── components/          # UI components (if needed)
```

### Key Features
1. **Conversation List** (left sidebar)
2. **Chat Bubbles** (main area)
   - User bubbles (right-aligned, light theme)
   - Assistant bubbles (left-aligned, dark theme)
   - Epistemic indicators (badges for claims/gaps)
3. **Input Area** (bottom)
4. **Navbar** (top, shared with all pages)

### Libraries
- No heavy frameworks (vanilla JS)
- SSE for streaming
- CSS variables for theming

---

## Auth Considerations

- Current: Mock auth with session cookies
- Future: OpenID Connect
- GDPR: User can delete all their data (conversation cascade)

---

## Performance Considerations

1. **Streaming**: Use SSE for real-time response
2. **Pagination**: Messages paginated (20 per page)
3. **Background Tasks**: Re-evaluation is async, non-blocking
4. **Connection Pooling**: Use asyncpg for DB

---

## Open Questions / TODOs

- [ ] Define RGPD implementation for "delete all user data"
- [ ] Add rate limiting to chat endpoints
- [ ] Implement conversation search
- [ ] Add typing indicators
- [ ] Implement "mark as resolved" for gaps from chat