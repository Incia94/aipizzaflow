# Implementation Handoff
## PizzaFlow AI

**Status:** Implementation-Ready
**Architecture Phase:** Complete
**Next Phase:** Folder Structure → Python Class Design → Implementation

---

## Document Purpose

This document is the contract between the architecture phase and the implementation phase. It summarises what was designed, which specifications govern each implementation decision, the rules that must hold throughout implementation, and the definition of done.

---

## 1. Architecture Summary

PizzaFlow AI is a **layered modular monolith** with five bounded contexts, five services, five API operations, and six persistent entities.

**What it does:**
- Digitises restaurant ordering, billing, and payment.
- Converts completed transactions into objective business intelligence.
- Provides AI-powered business reasoning over that intelligence.

**What it does not do:**
- Manage the kitchen, inventory, staff, or suppliers.
- Perform calculations inside the LLM.
- Allow the frontend to contain business logic.
- Store analytics results or AI responses in the database.

**The central insight:** Every context owns one transformation. Every service implements one capability. Every API operation exposes one capability. Every entity belongs to one owner. Unidirectional flow from Menu → Order → Checkout → Analytics → AI.

---

## 2. Specifications to Follow

Implement in this order. Each document is the specification for the corresponding implementation artifact.

| Implementation Artifact | Governing Specification |
|---|---|
| Folder structure | `bounded_contexts.md` — one folder per context |
| SQLAlchemy models | `database_design.md` — six persistent entities |
| Business rules enforcement | `business_rules.md` — all validation rules |
| Python services | `services.md` — five services, one per context |
| FastAPI routes | `api_design.md` — five operations, input/output contracts |
| Pydantic schemas | `api_design.md` — request/response contracts |
| Analytics calculations | `functional_decomposition.md` — six business categories, five analytical dimensions |
| AI prompt construction | `system_architecture.md` — AI Workflow, Flow C |
| Error responses | `api_design.md` — §7 Error Model (five categories) |
| Cross-cutting concerns | `system_architecture.md` — §8 (config, logging, error handling, CORS, DB sessions) |

---

## 3. Implementation Rules

These rules must not be violated during implementation. Any temptation to break one is a signal to re-examine the architecture, not to work around it.

1. **Business logic belongs in services, never in routes.** FastAPI routes receive requests, call services, and return responses. Nothing more.

2. **The frontend contains no calculations.** All business calculations are performed server-side in Python.

3. **The LLM receives only pre-computed metrics.** AIService calls AnalyticsService before building the prompt. Raw database records never reach the prompt.

4. **Services do not call each other's databases.** A service accesses only its own entities. The exception is AnalyticsService, which reads across all entities — this is its declared responsibility.

5. **No new services without updating the specifications.** If implementation reveals the need for a new service, return to `services.md` and `bounded_contexts.md` first.

6. **No new API operations without updating the specifications.** Five operations is intentional. Adding a sixth requires an architecture decision, not a code decision.

7. **Unit prices are captured at order time.** OrderItem stores the price paid — it does not reference MenuItem's current price.

8. **Checkout completion is a single database transaction.** Order → Paid, Bill created, Payment created — atomically.

9. **The Business Intelligence Model is always computed, never cached.** AnalyticsService computes on every request. No materialised views, no stored results.

10. **Each file has one job.** The principle "keep every file small and focused" applies to every module.

---

## 4. Definition of Done

The implementation is complete when all of the following are true:

### Functional
- [ ] Customer can browse the menu, build an order, and complete checkout.
- [ ] Bill displays subtotal, GST (18%), and total payable amount.
- [ ] Payment method (Cash, Card, UPI) is recorded against the order.
- [ ] Dashboard displays Business Intelligence across all six categories.
- [ ] AI Advisor responds to natural language business questions using Business Intelligence.

### Architectural
- [ ] All 40 checks from the Architecture Consistency Review remain true after implementation.
- [ ] No business logic exists in FastAPI routes.
- [ ] No business logic exists in the React frontend.
- [ ] The LLM receives no raw database records.
- [ ] All five bounded contexts are implemented as separate modules.
- [ ] All five API operations are implemented as specified.
- [ ] All six domain entities are persisted as specified.
- [ ] Checkout completion is atomic (single database transaction).

### Quality
- [ ] All environment variables are in `.env` — nothing is hardcoded.
- [ ] CORS is configured for the React frontend.
- [ ] Error responses follow the five-category error model.
- [ ] The application starts cleanly from a fresh clone with documented setup steps.

---

## Architecture Principles Reference

The full list of 19 principles governing this system is in `architecture_principles.md`. The five principles most likely to require active attention during implementation:

| Principle | Why it matters during implementation |
|---|---|
| #5 — Backend produces data, frontend presents data | Most common violation: putting display logic in Python or calculation logic in React |
| #7 — Deterministic computation and AI reasoning are separate | Most common violation: passing raw query results to the LLM |
| #10 — Service exists only for a business capability | Most common violation: creating helper services, utility services |
| #12 — Validate once, trust thereafter | Most common violation: re-validating in AnalyticsService what Checkout already validated |
| #15 — Unidirectional flow | Most common violation: a service calling another service that is upstream of it |

---

*The architecture phase is complete. This document is the handoff to implementation. From this point, Claude Code's role is to faithfully translate the approved specifications into working code — not to make new design decisions.*
