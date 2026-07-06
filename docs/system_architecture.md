# System Architecture Specification
## PizzaFlow AI

**Stage:** System Architecture
**Status:** Approved
**Next Stage:** API Design

---

## Document Purpose

This document defines how the bounded contexts of PizzaFlow AI collaborate as a running system. It describes layers, interaction patterns, request flows, event flows, external systems, and cross-cutting concerns. It does not discuss API schemas, database table design, Python class signatures, or folder structures.

---

## 1. Architecture Goal

> PizzaFlow AI is a layered modular monolith in which each bounded context owns exactly one business transformation, all business logic runs server-side in Python, and the AI receives only pre-computed deterministic business intelligence — never raw data.

---

## 2. Architectural Style

**Choice: Modular Monolith with Layered Architecture**

**What this means:**
- One deployable unit. The entire backend runs as a single FastAPI process.
- Inside that process, each bounded context is a self-contained module with clear ownership boundaries, matching exactly the contexts defined in the Bounded Contexts Specification.
- Within each module, a clean layered structure: API layer → Service layer → Persistence layer.

The modular monolith is an architectural choice, not a deployment limitation. If future business requirements demand independent scalability, individual bounded contexts can be extracted into separate services with minimal domain changes.

**Why not microservices:**
Local development only. Distributed deployment adds infrastructure complexity without solving any business problem. Five bounded contexts with clean, sequential data flow do not require network-level isolation.

**Why not hexagonal or clean architecture:**
Those patterns are designed for large teams, complex domain inversion, and long-term framework independence. This is an MVP. The added ceremony produces no business value at this scale.

**Why not event-driven (message broker):**
Business events in this system are synchronous and sequential. There is no async processing, background workers, or fan-out that would justify a message bus. The event vocabulary defined in the Bounded Contexts Specification represents business transitions, not technical messages.

---

## 3. System Layers

```
┌─────────────────────────────────────────────┐
│           Presentation Layer                │
│   React + Vite (browser)                    │
│   Pages: Home, Place Order, Bill,           │
│           Dashboard, AI Advisor             │
└─────────────────────────────────────────────┘
                     │
                  HTTP
                     │
┌─────────────────────────────────────────────┐
│              API Layer                      │
│   FastAPI — routes, request validation,     │
│   response serialization                    │
│   (no business logic)                       │
└─────────────────────────────────────────────┘
                     │
               service calls
                     │
┌─────────────────────────────────────────────┐
│             Service Layer                   │
│   Business capabilities implemented by      │
│   the five bounded contexts:                │
│                                             │
│   • Reference Context (Menu)                │
│   • Order Context                           │
│   • Checkout Context                        │
│   • Analytics Context                       │
│   • AI Advisor Context                      │
│                                             │
│   (all business logic lives here)           │
└─────────────────────────────────────────────┘
                     │
             ORM queries
                     │
┌─────────────────────────────────────────────┐
│           Persistence Layer                 │
│   SQLAlchemy ORM                            │
│   PostgreSQL (Supabase)                     │
└─────────────────────────────────────────────┘
                     │
          external integrations
                     │
┌─────────────────────────────────────────────┐
│           External Services                 │
│   Menu File (CSV/Excel)                     │
│   OpenRouter API                            │
└─────────────────────────────────────────────┘
```

**Layer responsibilities:**

| Layer | Responsibility | What it must never do |
|---|---|---|
| Presentation | Render UI, call API, display data | Contain business logic or calculations |
| API | Receive requests, validate input shape, call services, return responses | Contain business logic |
| Service | Implement business capabilities, enforce business rules, perform all calculations | Access the database directly (uses Persistence layer) |
| Persistence | Manage database sessions, execute queries, map ORM models | Contain business logic |
| External Services | Provide menu data, provide LLM reasoning | Be called directly from Presentation or Persistence |

---

## 4. Context Interaction Model

All five contexts exist within the Service Layer. They interact in a strict downstream pipeline.

```
Reference Context (Menu)
        │
        │  provides menu data (read-only)
        ▼
Order Context
        │
        │  Order Confirmed
        ▼
Checkout Context
        │
        │  Transaction Completed
        ▼
Analytics Context
        │
        │  Business Intelligence (on request)
        ▼
AI Advisor Context
```

**Rule:**
> A context may depend only on contexts whose published outputs it explicitly consumes.

No context reaches backwards. No cyclic dependencies exist. Downstream contexts receive output from upstream contexts — they never push data back or call into a context that has not declared them as a consumer.

---

## 5. Request Flow

### Flow A — Restaurant Operations

```
React (Place Order)
        │  Menu Request
        ▼
Reference Context → returns available menu items
        │
        ▼
React (customer builds and confirms order)
        │  Order Submission
        ▼
Order Context → creates Pending order
        │
        ▼
React (Bill page — customer reviews and pays)
        │  Checkout Request
        ▼
Checkout Context
        ├── validates transaction
        ├── calculates bill (GST applied)
        ├── records payment
        └── finalizes transaction (order → Paid)
        │
        ▼
React (confirmed bill displayed)
```

---

### Flow B — Business Intelligence

```
React (Dashboard)
        │  Analytics Request
        ▼
Analytics Context
        ├── retrieves Paid transactions
        ├── applies filters
        ├── aggregates and calculates
        └── produces Business Intelligence Model
        │
        ▼
React (renders KPI cards, charts, tables)
```

---

### Flow C — AI Advisor

```
React (AI Advisor)
        │  AI Query
        ▼
AI Advisor Context
        ├── requests Business Intelligence from Analytics Context (internal call)
        ├── assembles structured prompt
        └── calls OpenRouter API
        │
        ▼
OpenRouter → returns reasoning and recommendation
        │
        ▼
React (displays AI response)
```

*The AI Advisor calls the Analytics Context directly within the Service Layer. The Presentation Layer makes one request — it does not call Analytics separately for the AI flow.*

---

## 6. Event Flow

```
Customer confirms order
        │
        ▼  [Order Confirmed]
Checkout Context receives a Pending order
        │
Payment is processed
        │
        ▼  [Transaction Completed]
Paid transaction is persisted and available
        │
Analytics Context computes Business Intelligence
        │
        ▼  [Business Intelligence Ready]
AI Advisor Context receives Business Intelligence on request
        │
Reasoning applied over Business Intelligence
        │
        ▼  [AI Response Generated]
Natural language response returned to Rajan
```

**Business events represent domain state transitions. They are architectural concepts, not transport mechanisms.** Today they are synchronous in-process transitions. If future requirements introduce async processing, the event names and business meanings remain unchanged — only the transport mechanism changes.

---

## 7. External Systems

| System | Consumed By | Nature | Direction |
|---|---|---|---|
| Menu File (CSV/Excel) | Reference Context | Read-only at application startup | Inbound |
| OpenRouter API | AI Advisor Context | LLM reasoning on demand | Outbound |

No other external systems exist in this version.

---

## 8. Cross-Cutting Concerns

These concerns affect every layer but belong to no single bounded context.

| Concern | Responsibility |
|---|---|
| **Configuration** | All environment variables (database URL, OpenRouter API key, etc.) are loaded from a `.env` file at startup. No values are hardcoded anywhere in the system. |
| **Error Handling** | FastAPI exception handlers produce consistent, structured error responses. Business errors are distinct from system errors. |
| **Logging** | Request/response logging at the API layer. Significant business events logged at the service layer. |
| **Database Session Management** | SQLAlchemy session lifecycle is managed at the API layer and injected into services as needed. No service manages its own database session. |
| **CORS** | FastAPI CORS middleware configured to allow requests from the React frontend. |

*Note: Validation is not a cross-cutting concern. Interactive Validation is owned by the Order Context. Transaction Validation is owned by the Checkout Context. Each enforces its own rules at the appropriate stage.*

---

## 9. Architecture Principles Applied

| Principle | Where Applied |
|---|---|
| One bounded context = one business transformation | Each context in the Service Layer owns exactly one transformation with one clearly defined output |
| Unidirectional Flow | All information flows downstream: Menu → Order → Checkout → Analytics → AI. No backwards calls. |
| Backend produces data. Frontend presents data. | API Layer returns data objects. React renders them. No rendering logic in Python. |
| Deterministic computation and AI reasoning are separate | Analytics Context calculates; AI Advisor Context reasons. AI Advisor never calculates. |
| Validate once, trust thereafter | Checkout validates; Analytics and AI consume already-validated, Paid data |
| A service exists only if it implements a business capability | Service Layer is organised by bounded context, not by utility function |
| Business Capability Test | PromptBuilder is internal to AI Advisor Context. It does not appear as an architectural component. |

---

## 10. Out of Scope

The following are explicitly excluded from this architecture and should not be assumed as oversights.

- Microservices or distributed deployment
- Message broker or event bus (Kafka, RabbitMQ, etc.)
- Asynchronous background processing or task queues
- External payment gateway integration
- Authentication or authorisation
- Multi-tenancy
- Kitchen management or kitchen display system
- Inventory management
- Staff scheduling
- Delivery management
- Response caching
- Rate limiting

---

*This document is the approved specification for the System Architecture stage. The next stage is API Design.*
