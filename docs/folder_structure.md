# Folder Structure
## PizzaFlow AI

**Stage:** Folder Structure
**Status:** Approved
**Derived From:** `bounded_contexts.md`, `python_class_design.md`
**Next Stage:** Implementation

---

## Document Purpose

This folder structure is not designed — it is derived. Every directory and file placement follows mechanically from the architecture decisions already approved. No new architectural decisions are made here.

If the placement of any file is unclear, the answer is always in `bounded_contexts.md`: find which context owns the class, and that is where the file lives.

---

## Derivation Rules

### Rule 1 — One bounded context = one package

```
contexts/
    reference/
    order/
    checkout/
    analytics/
    ai_advisor/
```

Preserves Principle 8: every bounded context is implemented as a separate module.

### Rule 2 — Everything owned by a context lives inside that context

```
order/
    entities/
    repositories/
    schemas/
    service.py
    routes.py
```

Not a flat `models/`, `services/`, `schemas/` shared across the whole project. That would destroy the ownership boundaries.

### Rule 3 — Shared means genuinely shared

```
shared/
    config/
    database/
    exceptions/
```

No class migrates to `shared/` because another context wants to use it. Shared means it belongs to no context.

### Rule 4 — The frontend mirrors the backend bounded contexts

Feature-based architecture. The frontend is organised by business capability, not by technical layer.

```
features/
    order/
    checkout/
    analytics/
    ai/
```

The Reference Context (menu) is not a standalone frontend feature — menu data is consumed within the order flow.

### Rule 5 — Top-level infrastructure is unambiguous

```
backend/
frontend/
docs/
tests/
scripts/
```

---

## Backend Structure

```
backend/
│
├── app/
│   │
│   ├── contexts/
│   │   │
│   │   ├── reference/
│   │   │   ├── entities/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   ├── service.py
│   │   │   └── routes.py
│   │   │
│   │   ├── order/
│   │   │   ├── entities/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   ├── service.py
│   │   │   └── routes.py
│   │   │
│   │   ├── checkout/
│   │   │   ├── entities/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   ├── service.py
│   │   │   └── routes.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── models/          ← BI hierarchy (not ORM — Pydantic data classes)
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   ├── service.py
│   │   │   └── routes.py
│   │   │
│   │   └── ai_advisor/
│   │       ├── schemas/
│   │       ├── service.py
│   │       └── routes.py
│   │
│   ├── shared/
│   │   ├── config/              ← Settings (loaded from .env)
│   │   ├── database/            ← SQLAlchemy engine, session factory, Base
│   │   └── exceptions/          ← Five exception classes
│   │
│   └── main.py                  ← FastAPI application, router registration, startup
│
└── requirements.txt
```

**Note on `analytics/models/`:** These are not ORM entities. They are the Pydantic data classes that form the Business Intelligence hierarchy (`RevenueMetrics`, `SalesMetrics`, …, `BusinessIntelligenceModel`). The directory is named `models/` rather than `entities/` because nothing in this context is persisted — these classes model computed output, not database rows.

**Note on routes:** Routes are the API surface of their bounded context. They belong inside the context, not in a global `routes/` directory.

---

## Frontend Structure

```
frontend/
│
├── src/
│   │
│   ├── features/
│   │   ├── order/               ← Place Order page (menu + order builder)
│   │   ├── checkout/            ← Bill page + payment confirmation
│   │   ├── analytics/           ← Dashboard (all six BI categories)
│   │   └── ai/                  ← AI Advisor chat interface
│   │
│   ├── components/              ← Shared UI primitives only (no business logic)
│   ├── api/                     ← API client (one function per backend operation)
│   └── main.tsx
│
└── package.json
```

---

## Tests Structure

```
tests/
│
└── contexts/
    ├── reference/
    ├── order/
    ├── checkout/
    ├── analytics/
    └── ai_advisor/
```

Tests mirror the context structure. Each context's tests live alongside its implementation.

---

## Top-Level Structure

```
RESTURANT_MANAGEMENT/
│
├── backend/
├── frontend/
├── docs/
├── tests/
└── scripts/                     ← Database seed scripts, CSV loader utilities
```

---

## File Placement Guide

When placing a new file during implementation, ask: which bounded context owns this class?

| Class Type | Location |
|---|---|
| Entity (SQLAlchemy) | `contexts/{context}/entities/` |
| Repository Interface | `contexts/{context}/repositories/` |
| Request Schema (Pydantic) | `contexts/{context}/schemas/` |
| Response Schema (Pydantic) | `contexts/{context}/schemas/` |
| Service | `contexts/{context}/service.py` |
| Routes | `contexts/{context}/routes.py` |
| BI Data Class | `contexts/analytics/models/` |
| Exception | `shared/exceptions/` |
| Settings | `shared/config/` |
| Database session / Base | `shared/database/` |

If a file does not belong to any single bounded context, it belongs to `shared/`. If it belongs to `shared/` and there is already a class doing the same job, it should not exist.

---

*This document is derived, not designed. The architecture is in `bounded_contexts.md`. This document only records where each part of that architecture lives on disk.*
